import os
from enum import Enum
from time import sleep

from PySide6.QtCore import QObject, Signal, QThreadPool, Slot
from PySide6.QtWidgets import QMessageBox

from controllers.arduino_controller import ArduinoController
from controllers.electronic_load_controller import ElectronicLoadController
from models.test_file_model import TestData, Step
from utils.config_manager import ConfigManager
from utils.constants import TEST_FILES_DIR
from utils.delay_manager import DelayManager
from utils.monitor_worker import MonitorWorker
from utils.report_file_util import generate_report_file
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


def show_custom_dialog(text: str, message_type: QMessageBox.Icon) -> None:
    dialog = QMessageBox()
    dialog.setWindowTitle(
        "INFO" if message_type == QMessageBox.Icon.Information else "ERROR"
    )
    dialog.setText(text)
    dialog.setStandardButtons(
        QMessageBox.StandardButton.Ok
        if message_type == QMessageBox.Icon.Information
        else QMessageBox.StandardButton.Close
    )
    dialog.setIcon(message_type)
    dialog.exec()


class TestController(QObject):
    state_changed = Signal(str)
    serial_number_updated = Signal(str)
    current_step_changed = Signal(str, float, int)

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
        self.test_result_data = dict()
        self.test_sequence_status: list[bool] = []
        self.temp_data_file = None

        # Instances
        self.config = ConfigManager()
        self.electronic_load_controller = ElectronicLoadController()
        self.arduino_controller = ArduinoController()
        self.worker_signals = WorkerSignals()
        self.thread_pool = QThreadPool()
        self.monitoring_worker = None
        self.delay_manager = DelayManager()

        # Signals
        self.worker_signals.update_output.connect(self.__update_output_display)
        self.delay_manager.delay_completed.connect(self.__on_delay_completed)

        # Monitor
        if self.electronic_load_controller.conn_status:
            self.__start_monitoring()

    @Slot()
    def start_test_sequence(self):
        if self.state in [TestState.RUNNING, TestState.PAUSED, TestState.WAITKEY]:
            return

        print("START")
        # if not self.__check_instruments():
        #     return

        if self.serial_number == "":
            self.__update_serial_number(False)

        if self.state is TestState.PASSED and not self.is_single_step_test:
            self.__update_serial_number(True)

        self.__update_state(TestState.RUNNING)
        if not self.is_single_step_test:
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

        self.__run_steps()

    @Slot(int)
    def setup_single_run(self, step_index):
        """
        Setups a single step test and starts the test sequence.
        :param step_index: Index of the Step.
        :return: None.
        """
        self.is_single_step_test = True
        self.current_step_index = step_index
        self.start_test_sequence()

    @Slot()
    def toggle_test_pause_state(self):
        """
        Toggle the current state between RUNNING and PAUSED.
        :return:
        """
        if self.state not in [TestState.RUNNING, TestState.PAUSED]:
            return
        self.delay_manager.pause_resume()
        self.__update_state(TestState.RUNNING if self.state is TestState.PAUSED else TestState.PAUSED)

    @Slot()
    def cancel_test_sequence(self):
        """
        Cancels the current test sequence.
        :return: None.
        """
        if self.state not in [TestState.RUNNING, TestState.PAUSED, TestState.WAITKEY]:
            return
        print("CANCEL")
        self.__update_state(TestState.CANCELED)
        self.__reset_setup()

    @Slot()
    def __on_delay_completed(self):
        if self.state is not TestState.CANCELED:
            self.__validate_step_values()
            self.current_step_index += 1
            self.__run_steps()

    @Slot()
    def __update_output_display(self):
        """
        Updates the channel displays (voltage) in a dedicated thread.
        :return: None.
        """
        for channel in self.channel_list:
            voltage_value = self.electronic_load_controller.get_channel_value(channel.channel_id)
            channel.set_values((float(voltage_value), None))

    def __run_steps(self):
        sleep(1)
        if self.is_single_step_test:
            steps = [self.test_data.steps[self.current_step_index]]
        else:
            steps = self.test_data.steps

        if self.current_step_index < len(steps):
            current_step: Step = steps[self.current_step_index]
            self.arduino_controller.set_input_source(current_step.input_source, self.test_data.input_type)
            self.current_step_changed.emit(current_step.description, current_step.duration, self.current_step_index)

            match current_step.step_type:
                case 1:
                    for channel_id, param_id in current_step.channel_params.items():
                        channel_params = next((param for param in self.test_data.params if param.id == param_id), None)
                        if channel_params:
                            self.electronic_load_controller.set_channel_current(channel_id, channel_params.ia)
                            for channel in self.channel_list:
                                channel.set_values((None, channel_params.ia))

                    if current_step.duration == 0:
                        self.__update_state(TestState.WAITKEY)
                    else:
                        self.delay_manager.start_delay(current_step.duration * 1000)

                case 2:
                    pass

                case 3:
                    pass

        else:
            self.electronic_load_controller.toggle_active_channels_input(
                [key for key in self.test_data.channels.keys()], False)
            if self.temp_data_file:
                self.temp_data_file.close()
                os.remove(self.temp_data_file.name)

            if self.state is not TestState.CANCELED:
                self.__update_state(TestState.FAILED if False in self.test_sequence_status else TestState.PASSED)

            self.temp_data_file = generate_report_file(self.test_result_data)

            # if self.state is TestState.PASSED and not self.is_single_step_test:
            if not self.is_single_step_test:  # TESTE
                with open(file=f"{self.config.get(TEST_FILES_DIR)}/{self.test_data.group}/{self.serial_number}.txt",
                          mode="w", encoding="utf-8") as test_file:
                    test_file.write(self.__read_temp_data_file())
            print("DONE")
            self.__reset_setup()

    def __read_temp_data_file(self) -> str:
        if self.temp_data_file:
            with open(self.temp_data_file.name, "r", encoding="utf-8") as file:
                return file.read()
        return ""

    def __validate_step_values(self):
        step_pass = False
        current_step_data = []
        current_step = self.test_data.steps[self.current_step_index]

        for channel in self.channel_list:
            values = channel.get_values()
            channel_data = {}
            channel_params = None
            for param_id in current_step.channel_params.values():
                channel_params = next((param for param in self.test_data.params if param.id == param_id), None)
                if channel_params:
                    channel_data = {
                        "channel_id": str(channel.channel_id),
                        "outcome_voltage": values.get("voltage", 0.0),
                        "lower_voltage": channel_params.va,
                        "upper_voltage": channel_params.vb,
                        "load": values.get("current", 0.0),
                        "power": values.get("power", 0.0)
                    }
            if channel_params:
                if channel_params.va <= values.get("voltage", 0.0) <= channel_params.vb:
                    step_pass = True

            current_step_data.append(channel_data)

        self.test_sequence_status.append(step_pass)
        self.__handle_test_results_data(current_step, tuple(current_step_data), step_pass)

    def __handle_test_results_data(self, current_step: Step, data: tuple, step_status: bool):
        step_data = {
            "description": current_step.description,
            "step_status": step_status,
            "step_type": current_step.step_type,
            "channels_data": data
        }
        self.test_result_data["steps_result"].append(step_data)

    def __reset_setup(self):
        self.electronic_load_controller.reset_instrument()
        self.electronic_load_controller.toggle_active_channels_input(
            [key for key in self.test_data.channels.keys()], False)
        self.arduino_controller.set_active_pin(True)
        self.arduino_controller.active_input_source = 0
        self.delay_manager.paused = False
        self.delay_manager.remaining_time = 0
        self.is_single_step_test = False
        self.test_sequence_status.clear()

    def __update_state(self, new_state: TestState):
        """
        Updates the current test state.
        :param new_state: TestState to be set.
        :return: None.
        """
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(new_state.value)

    def __update_serial_number(self, is_increment: bool):
        """
        Set the serial number to zeros or increments the current number by 1.
        :param is_increment: Case true, increments the number.
        :return: None.
        """
        new_value = str(int(self.serial_number) + 1) if is_increment else ""
        self.serial_number = new_value.zfill(8)
        self.serial_number_updated.emit(self.serial_number)

    def __start_monitoring(self):
        """
        Creates a new thread worker case it's None, else resume it.
        :return: None.
        """
        if self.monitoring_worker is None:
            self.monitoring_worker = MonitorWorker(self.worker_signals)
            self.thread_pool.start(self.monitoring_worker)
        else:
            self.monitoring_worker.resume()

    def __check_instruments(self) -> bool:
        """
        Checks for the instruments connection.
        :return: Bool representing the instruments state.
        """
        if not self.electronic_load_controller.conn_status:
            show_custom_dialog("IT8700 : INSTRUMENT NOT FOUND.", QMessageBox.Icon.Critical)
            return False
        if not self.arduino_controller.check_connection():
            show_custom_dialog("ARDUINO : INSTRUMENT NOT FOUND.", QMessageBox.Icon.Critical)
            return False
        return True
