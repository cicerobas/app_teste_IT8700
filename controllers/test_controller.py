import os
from enum import Enum
from time import sleep

from PySide6.QtCore import QObject, Signal, QThreadPool, Slot, QTimer
from PySide6.QtWidgets import QMessageBox

from controllers.arduino_controller import ArduinoController
from controllers.electronic_load_controller import ElectronicLoadController
from models.test_file_model import TestData, Step, Param
from utils.config_manager import ConfigManager
from utils.constants import TEST_FILES_DIR
from utils.delay_manager import DelayManager
from utils.monitor_worker import MonitorWorker
from utils.report_file_util import generate_report_file
from utils.window_utils import show_custom_dialog
from views.channel_monitor_view import ChannelMonitorView


class TestState(Enum):
    RUNNING = "TESTING"
    PAUSED = "PAUSED"
    CANCELED = "CANCELED"
    PASSED = "PASS"
    FAILED = "FAIL"
    WAITKEY = "PRESS [ENTER] TO CONTINUE"
    NONE = ""


class WorkerSignals(QObject):
    update_output = Signal()


class TestController(QObject):
    state_changed = Signal(str)
    serial_number_updated = Signal(str)
    current_step_changed = Signal(str, float, int)
    result_file_updated = Signal(str)

    def __init__(self, test_data: TestData):
        super().__init__()
        # Data
        self.test_data = test_data
        self.channel_list: list[ChannelMonitorView] = []
        self.state: TestState = TestState.NONE
        self.serial_number: str = ""
        self.tester_id: str = ""
        self.is_single_step_test: bool = False
        self.current_step_index: int = 0
        self.single_step_index: int = -1
        self.test_result_data = dict()
        self.test_sequence_status: list[bool] = []
        self.temp_data_file = None
        self.serial_number_needs_increment = False

        # Instances
        self.config = ConfigManager()
        self.electronic_load_controller = ElectronicLoadController()
        self.arduino_controller = ArduinoController()
        self.worker_signals = WorkerSignals()
        self.thread_pool = QThreadPool()
        self.monitoring_worker = None
        self.delay_manager = DelayManager()

        # Signals
        self.worker_signals.update_output.connect(self._update_output_display)
        self.delay_manager.delay_completed.connect(self._on_delay_completed)

        # Monitor
        if self.electronic_load_controller.conn_status:
            self._start_monitoring()

    @Slot()
    def start_test_sequence(self) -> None:
        """Verifies the conditions to start the test sequence."""
        if self.state in [TestState.RUNNING, TestState.PAUSED, TestState.WAITKEY]:
            return

        if not self._check_instruments():
            return

        if self.serial_number == "":
            self._update_serial_number(self.serial_number_needs_increment)

        if self.state is TestState.PASSED:
            self._update_serial_number(self.serial_number_needs_increment)

        self._update_state(TestState.RUNNING)
        self.current_step_index = 0
        self.test_result_data.update(
            group=self.test_data.group,
            model=self.test_data.model,
            customer=self.test_data.customer,
            tester_id=self.tester_id,
            serial_number=self.serial_number,
            steps_result=[]
        )

        self.electronic_load_controller.toggle_active_channels_input(
            [key for key in self.test_data.channels.keys()], True)

        self._run_steps()

    @Slot(int)
    def setup_single_run(self, step_id: int) -> None:
        """Setups a single step test and starts the test sequence."""
        for index, step in enumerate(self.test_data.steps):
            if step.id == step_id:
                self.single_step_index = index
                self.is_single_step_test = True
                self.serial_number_needs_increment = False
                self.start_test_sequence()

    @Slot()
    def toggle_test_pause_state(self) -> None:
        """Toggle the current state between RUNNING and PAUSED."""
        if self.state not in [TestState.RUNNING, TestState.PAUSED]:
            return
        self.delay_manager.pause_resume()
        self._update_state(TestState.RUNNING if self.state is TestState.PAUSED else TestState.PAUSED)

    @Slot()
    def continue_sequence(self) -> None:
        self._update_state(TestState.RUNNING)
        self._on_delay_completed()

    @Slot()
    def cancel_test_sequence(self) -> None:
        if self.state not in [TestState.RUNNING, TestState.PAUSED, TestState.WAITKEY, TestState.NONE]:
            return
        self._update_state(TestState.CANCELED)
        self.reset_setup()

    @Slot()
    def _on_delay_completed(self) -> None:
        """Called by the delay manager, runs the next test step."""
        if self.state is not TestState.CANCELED:
            self._validate_direct_current_step_values()
            self.current_step_index += 1
            self._run_steps()

    @Slot()
    def _update_output_display(self) -> None:
        """Updates each [channel_view] voltage in a dedicated thread."""
        for channel in self.channel_list:
            voltage_value = self.electronic_load_controller.get_channel_value(channel.channel_id)
            channel.set_values((float(voltage_value), None))

    def _run_steps(self) -> None:
        """
        Verifies the step list and runs the tests.
        At the end of the sequence, verifies the test condition [PASS or FAIL] and handles the test file.
        """
        sleep(1)
        if self.is_single_step_test:
            steps = [self.test_data.steps[self.single_step_index]]
        else:
            steps = self.test_data.steps

        if self.current_step_index < len(steps):
            current_step: Step = steps[self.current_step_index]
            self.arduino_controller.set_input_source(current_step.input_source, self.test_data.input_type)
            self.current_step_changed.emit(current_step.description, current_step.duration, self.current_step_index)
            self._update_display_limits(current_step)
            match current_step.step_type:
                case 1:
                    self._run_direct_current_step(current_step)
                case 2:
                    self._set_current_limiting_step(current_step)
                case 3:
                    self._set_short_test_step(current_step)

        else:
            self.electronic_load_controller.toggle_active_channels_input(
                [key for key in self.test_data.channels.keys()], False)
            if self.temp_data_file:
                self.temp_data_file.close()
                os.remove(self.temp_data_file.name)

            if self.state is not TestState.CANCELED:
                self._update_state(TestState.FAILED if False in self.test_sequence_status else TestState.PASSED)

            self.temp_data_file = generate_report_file(self.test_result_data)
            self.result_file_updated.emit(self._read_temp_data_file())
            if self.state is TestState.PASSED and not self.is_single_step_test:
                with open(file=f"{self.config.get(TEST_FILES_DIR)}/{self.test_data.group}/{self.serial_number}.txt",
                          mode="w", encoding="utf-8") as test_file:
                    test_file.write(self._read_temp_data_file())
                self._update_serial_number(True)
            self._update_output_display()
            self.arduino_controller.buzzer()
            self.reset_setup()

    def _update_display_limits(self, current_step: Step) -> None:
        """Updates the limits on each [channel_view] slider."""
        for channel_id, param_id in current_step.channel_params.items():
            channel_view = self._get_channel_view_by_id(channel_id)
            channel_params = self._get_channel_params_by_id(param_id)
            if current_step.step_type == 1:
                channel_view.set_limits(channel_params.va, channel_params.vb)
            else:
                lower_value = channel_params.va * 0.5
                upper_value = channel_params.va + lower_value
                channel_view.set_limits(round(lower_value, 2), round(upper_value, 2))

    def _read_temp_data_file(self) -> str:
        if self.temp_data_file:
            with open(self.temp_data_file.name, "r", encoding="utf-8") as file:
                return file.read()
        return ""

    def _set_short_test_step(self, current_step: Step) -> None:
        self._update_state(TestState.NONE)
        channels_data = []
        for channel_id, param_id in current_step.channel_params.items():
            channels_data.append({'id': channel_id, 'param_id': param_id, 'shutdown': False, 'recovery': False})
        self._run_short_test(channels_data)

    def _run_short_test(self, data: list[dict], current_index: int = 0, current_cycle: int = 0) -> None:
        """Sets the channel for [SHORT] mode and recursively verifies both states [shutdown, recovery]."""
        if self.state is TestState.CANCELED:
            return
        delay = 500
        if current_index < len(data):
            current_channel = data[current_index]
            channel_params = self._get_channel_params_by_id(current_channel["param_id"])
            if current_cycle == 0:
                self.electronic_load_controller.set_channel_current(current_channel["id"], channel_params.ia)

            current_channel_view = self._get_channel_view_by_id(current_channel["id"])
            channel_values = current_channel_view.get_display_values()
            voltage_read = channel_values["voltage"]
            if current_cycle < 20 and not current_channel["recovery"]:
                if voltage_read >= channel_params.va * 0.2 and not current_channel["shutdown"]:
                    self.electronic_load_controller.toggle_short_mode(current_channel["id"], True)
                elif voltage_read <= channel_params.va * 0.2 and not current_channel["shutdown"]:
                    current_channel["shutdown"] = True
                    self.electronic_load_controller.toggle_short_mode(current_channel["id"], False)
                elif voltage_read >= channel_params.va and current_channel["shutdown"] and not current_channel[
                    "recovery"]:
                    current_channel["recovery"] = True

                QTimer.singleShot(delay, lambda: self._run_short_test(data, current_index, current_cycle + 1))
            else:
                self.electronic_load_controller.set_channel_current(current_channel["id"], 0)
                QTimer.singleShot(delay, lambda: self._run_short_test(data, current_index + 1, 0))
        else:
            self._validate_short_test_step(data)
            self.current_step_index += 1
            self._run_steps()

    def _validate_short_test_step(self, data: list[dict]) -> None:
        """Validates the [SHORT] mode test, verifying the [recovery] and [shutdown] states."""
        step_pass = False
        channels_pass = []
        current_step_data = []
        current_step = self.test_data.steps[
            self.single_step_index if self.is_single_step_test else self.current_step_index]
        for channel in data:
            channel_data = {}
            channel_params = self._get_channel_params_by_id(channel["param_id"])
            if channel_params:
                channel_data = {
                    "channel_id": str(channel["id"]),
                    "shutdown": channel["shutdown"],
                    "recovery": channel["recovery"],
                    "voltage_ref": channel_params.va,
                    "load": channel_params.ia
                }
                channels_pass.append(channel["shutdown"] and channel["recovery"])

            step_pass = False not in channels_pass
            current_step_data.append(channel_data)
            self.test_sequence_status.append(step_pass)

        self._handle_test_results_data(current_step, tuple(current_step_data), step_pass)

    def _run_direct_current_step(self, current_step: Step) -> None:
        """Sets the channel current and handles the step delay."""
        for channel_id, param_id in current_step.channel_params.items():
            channel_params = self._get_channel_params_by_id(param_id)
            if channel_params:
                self.electronic_load_controller.set_channel_current(channel_id, channel_params.ia)
                channel_view = self._get_channel_view_by_id(channel_id)
                channel_view.set_values((None, channel_params.ia))

        if current_step.duration == 0:
            self._update_state(TestState.WAITKEY)
        else:
            self.delay_manager.start_delay(current_step.duration * 1000)

    def _set_current_limiting_step(self, current_step: Step) -> None:
        self._update_state(TestState.NONE)
        self._run_current_limiting_step(current_step.channel_params, None, None)

    def _run_current_limiting_step(self, channel_params: dict[int, int], data: list[dict] | None,
                                   current_load: float | None,
                                   current_index: int = 0) -> None:
        """Sets the channel for testing and recursively increases the current until the limit is reached."""

        if self.state is TestState.CANCELED:
            return
        if not data:
            channels_data = []
            for channel_id, param_id in channel_params.items():
                channels_data.append({'id': channel_id, 'param_id': param_id, 'limit': 0.0, 'done': False})
        else:
            channels_data = data

        if current_index < len(channels_data):

            current_channel = channels_data[current_index]
            current_channel_view = self._get_channel_view_by_id(current_channel["id"])
            params = self._get_channel_params_by_id(current_channel["param_id"])
            if not current_load:
                current_load = params.ia

            channel_values = current_channel_view.get_display_values()
            voltage_read = channel_values["voltage"]
            if not current_channel["done"]:
                if voltage_read >= params.va and current_load <= params.ib:
                    current_load += 0.01
                    self.electronic_load_controller.set_channel_current(current_channel["id"], current_load)
                    current_channel_view.set_values((None, current_load))
                    QTimer.singleShot(100, lambda: self._run_current_limiting_step(channel_params, channels_data,
                                                                                   current_load, current_index))
                else:
                    current_channel["limit"] = current_load
                    self.electronic_load_controller.set_channel_current(current_channel["id"], params.ia)
                    current_channel_view.set_values((None, params.ia))
                    current_channel["done"] = True
                    QTimer.singleShot(100, lambda: self._run_current_limiting_step(channel_params, channels_data,
                                                                                   params.ia, current_index))
            else:
                if voltage_read <= params.va:
                    QTimer.singleShot(100, lambda: self._run_current_limiting_step(channel_params, channels_data,
                                                                                   params.ia, current_index))
                else:
                    QTimer.singleShot(100, lambda: self._run_current_limiting_step(channel_params, channels_data,
                                                                                   params.ia, current_index + 1))
        else:
            self._update_state(TestState.RUNNING)
            self._validate_current_limiting_step_values(channels_data)
            self.current_step_index += 1
            self._run_steps()

    def _validate_current_limiting_step_values(self, data: list[dict]) -> None:
        """Validates and creates a dict with the current limiting test values."""
        step_pass = False
        channels_pass = []
        current_step_data = []
        current_step = self.test_data.steps[
            self.single_step_index if self.is_single_step_test else self.current_step_index]
        for channel in data:
            channel_data = {}
            channel_params = self._get_channel_params_by_id(channel["param_id"])
            if channel_params:
                channel_data = {
                    "channel_id": str(channel["id"]),
                    "under_voltage": channel_params.va,
                    "load_upper": channel_params.ib,
                    "load_lower": channel_params.ia,
                    "load": channel["limit"]
                }
                channels_pass.append(True if channel_params.ia < channel["limit"] <= channel_params.ib else False)

            step_pass = False not in channels_pass
            self.test_sequence_status.append(step_pass)
            current_step_data.append(channel_data)

        self._handle_test_results_data(current_step, tuple(current_step_data), step_pass)

    def _validate_direct_current_step_values(self) -> None:
        """Validates and creates a dict with the direct current test values."""
        step_pass = False
        channels_pass = []
        current_step_data = []
        current_step = self.test_data.steps[
            self.single_step_index if self.is_single_step_test else self.current_step_index]
        for channel_id, param_id in current_step.channel_params.items():
            channel_view = self._get_channel_view_by_id(channel_id)
            values = channel_view.get_display_values()
            channel_data = {}
            channel_params = self._get_channel_params_by_id(param_id)
            if channel_params:
                channel_data = {
                    "channel_id": str(channel_view.channel_id),
                    "outcome_voltage": values.get("voltage", 0.0),
                    "lower_voltage": channel_params.va,
                    "upper_voltage": channel_params.vb,
                    "load": values.get("current", 0.0),
                    "power": values.get("power", 0.0)
                }

                channels_pass.append(
                    True if channel_params.va <= values.get("voltage", 0.0) <= channel_params.vb else False)

            step_pass = False not in channels_pass
            self.test_sequence_status.append(step_pass)
            current_step_data.append(channel_data)

        self._handle_test_results_data(current_step, tuple(current_step_data), step_pass)

    def _handle_test_results_data(self, current_step: Step, data: tuple, step_status: bool) -> None:
        step_data = {
            "description": current_step.description,
            "step_status": step_status,
            "step_type": current_step.step_type,
            "channels_data": data
        }
        self.test_result_data["steps_result"].append(step_data)

    def reset_setup(self) -> None:
        self.electronic_load_controller.reset_instrument()
        self.electronic_load_controller.toggle_active_channels_input(
            [key for key in self.test_data.channels.keys()], False)
        self.arduino_controller.setup_active_pin(True)
        self.arduino_controller.active_pin = 0
        self.delay_manager.paused = False
        self.delay_manager.remaining_time = 0
        self.is_single_step_test = False
        self.single_step_index = -1
        self.test_sequence_status.clear()

    def _update_state(self, new_state: TestState) -> None:
        """Updates the current test state."""
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(new_state.value)

    def _update_serial_number(self, is_increment: bool) -> None:
        """Set the [serial_number] to zeros or increments the current number by 1."""
        new_value = str(int(self.serial_number) + 1) if is_increment else self.serial_number
        self.serial_number = new_value.zfill(8)
        self.serial_number_updated.emit(self.serial_number)

    def _start_monitoring(self) -> None:
        """Creates a new thread worker case it's None, else resume it."""
        if self.monitoring_worker is None:
            self.monitoring_worker = MonitorWorker(self.worker_signals)
            self.thread_pool.start(self.monitoring_worker)
        else:
            self.monitoring_worker.resume()

    def _check_instruments(self) -> bool:
        """Checks for the instruments connection."""
        if not self.electronic_load_controller.conn_status:
            show_custom_dialog("IT8700 : INSTRUMENT NOT FOUND.", QMessageBox.Icon.Critical)
            return False
        if not self.arduino_controller.check_connection():
            show_custom_dialog("ARDUINO : INSTRUMENT NOT FOUND.", QMessageBox.Icon.Critical)
            return False
        return True

    def _get_channel_params_by_id(self, param_id: int) -> Param | None:
        return next((param for param in self.test_data.params if param.id == param_id), None)

    def _get_channel_view_by_id(self, channel_id: int) -> ChannelMonitorView | None:
        return next((channel_view for channel_view in self.channel_list if channel_view.channel_id == channel_id), None)
