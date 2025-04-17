from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QIntValidator, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLineEdit, QFormLayout, QPushButton, \
    QGridLayout, QLabel

from controllers.test_controller import TestController, TestState
from models.test_file_model import TestData
from utils.assets_path_util import resource_path
from views.channel_monitor_view import ChannelMonitorView

ICON_SIZE = QSize(20, 20)


def update_label_object_name(label: QLabel, status_name: str) -> None:
    label.setObjectName(status_name)
    label.style().unpolish(label)
    label.style().polish(label)
    label.update()


class TestRunTabView(QWidget):
    def __init__(self, test_data: TestData, test_controller: TestController):
        super().__init__()
        self.test_data: TestData = test_data
        self.test_controller = test_controller

        # Components
        self.serial_number_field = QLineEdit()
        self.serial_number_field.setValidator(QIntValidator(0, 99999999, self))
        self.tester_id_field = QLineEdit()
        self.run_button = QPushButton(icon=QIcon(resource_path("assets/icons/play.svg")), text=" RUN", parent=self)
        self.stop_button = QPushButton(icon=QIcon(resource_path("assets/icons/stop.svg")), text=" STOP", parent=self)
        self.run_button.setIconSize(ICON_SIZE)
        self.stop_button.setIconSize(ICON_SIZE)
        self.current_state_label = QLabel("")
        self.current_state_label.setObjectName("state_label")
        self.current_step_label = QLabel("")
        self.current_step_label.setObjectName("step_label")
        self.timer_label = QLabel("0.0s")
        self.steps_progress_label = QLabel(f"0/{len(self.test_data.steps)}")
        self.group_label = QLabel(self.test_data.group)
        self.model_label = QLabel(self.test_data.model)
        self.customer_label = QLabel(self.test_data.customer)
        self.input_type_label = QLabel(self.test_data.input_type)

        # Signals
        self.run_button.clicked.connect(self.test_controller.start_test_sequence)
        self.stop_button.clicked.connect(self.test_controller.cancel_test_sequence)
        self.serial_number_field.textChanged.connect(self._set_serial_number)
        self.tester_id_field.textChanged.connect(self._set_tester_id)
        self.test_controller.state_changed.connect(self._update_status_label)
        self.test_controller.serial_number_updated.connect(self._update_serial_number_field)
        self.test_controller.current_step_changed.connect(self._set_step_info)
        self.test_controller.delay_manager.remaining_time_changed.connect(self._update_timer)

        for channel_id in self.test_data.channels.keys():
            channel_monitor = ChannelMonitorView(channel_id)
            channel_monitor.setProperty("class", "channel_monitor")
            self.test_controller.channel_list.append(channel_monitor)

        self.setLayout(self._setup_layout())

    @Slot(int)
    def _update_timer(self, remaining_time: int) -> None:
        self.timer_label.setText(f"{remaining_time / 1000}s")

    @Slot(str, float, int)
    def _set_step_info(self, description: str, duration: float, index: int) -> None:
        self.current_step_label.setText(description)
        self.timer_label.setText(f"{duration}s")
        self.steps_progress_label.setText(f"{index + 1}/{len(self.test_data.steps)}")

    @Slot(str)
    def _set_tester_id(self, value: str) -> None:
        self.test_controller.tester_id = value

    @Slot(str)
    def _set_serial_number(self, value: str) -> None:
        self.test_controller.serial_number = value.zfill(8)
        self.test_controller.serial_number_needs_increment = False

    @Slot(str)
    def _update_serial_number_field(self, value: str) -> None:
        self.serial_number_field.setText(value)

    @Slot(str)
    def _update_status_label(self, value: str) -> None:
        """Updates the status label text and it's objectName attribute."""
        self.current_state_label.setText(value)
        match self.test_controller.state:
            case TestState.PASSED | TestState.RUNNING:
                update_label_object_name(self.current_state_label, "label_green")
            case TestState.PAUSED | TestState.WAITKEY:
                update_label_object_name(self.current_state_label, "label_orange")
            case TestState.CANCELED | TestState.FAILED:
                update_label_object_name(self.current_state_label, "label_red")
            case _:
                update_label_object_name(self.current_state_label, "label_default")

        self._update_fields_state()

    def _update_fields_state(self) -> None:
        """Toggles the state of the buttons to match the state of the application"""
        state = self.test_controller.state
        if state is TestState.NONE:
            return

        self.serial_number_field.setReadOnly(True)
        self.tester_id_field.setReadOnly(True)
        if state in [TestState.RUNNING, TestState.PAUSED]:
            self.run_button.setIcon(
                QIcon(resource_path("assets/icons/pause.svg")) if state is TestState.RUNNING else QIcon(resource_path("assets/icons/play.svg")))
            self.run_button.setText(" PAUSE" if state is TestState.RUNNING else " CONTINUE")
            self.run_button.clicked.disconnect()
            self.run_button.clicked.connect(self.test_controller.toggle_test_pause_state)
        elif state is TestState.WAITKEY:
            self.run_button.setIcon(QIcon(resource_path("assets/icons/play.svg")))
            self.run_button.setText(" CONTINUE")
            self.run_button.clicked.disconnect()
            self.run_button.clicked.connect(self.test_controller.continue_sequence)
        else:
            self.serial_number_field.setReadOnly(False)
            self.tester_id_field.setReadOnly(False)
            self.run_button.setIcon(QIcon(resource_path("assets/icons/play.svg")))
            self.run_button.setText(" RUN")
            self.run_button.clicked.disconnect()
            self.run_button.clicked.connect(self.test_controller.start_test_sequence)

        self.run_button.setFocus()

    def _setup_layout(self) -> QHBoxLayout:
        # Actions
        action_buttons = QWidget()
        action_buttons.setFixedHeight(70)
        h_buttons_layout = QHBoxLayout(action_buttons)
        h_buttons_layout.addWidget(self.run_button)
        h_buttons_layout.addWidget(self.stop_button)

        # Setup
        test_setup_groupbox = QGroupBox("SETUP")
        test_setup_groupbox.setProperty("class", "left_panel_gb")
        test_setup_groupbox.setFixedWidth(450)
        f_test_setup_layout = QFormLayout(test_setup_groupbox)
        f_test_setup_layout.addRow("Serial Nº : ", self.serial_number_field)
        f_test_setup_layout.addRow("Tester : ", self.tester_id_field)
        f_test_setup_layout.addRow(action_buttons)

        # Info
        test_info_groupbox = QGroupBox("INFO")
        test_info_groupbox.setMaximumWidth(450)
        test_info_groupbox.setProperty("class", "left_panel_gb")
        v_test_info_layout = QVBoxLayout(test_info_groupbox)
        v_test_info_layout.setSpacing(10)
        h_timer_progress_layout = QHBoxLayout()
        h_timer_progress_layout.addWidget(self.steps_progress_label)
        h_timer_progress_layout.addWidget(self.timer_label, alignment=Qt.AlignmentFlag.AlignRight)
        f_test_info_layout = QFormLayout()
        f_test_info_layout.addRow("STATE:", self.current_state_label)
        f_test_info_layout.addRow("STEP:", self.current_step_label)
        v_test_info_layout.addLayout(f_test_info_layout)
        v_test_info_layout.addLayout(h_timer_progress_layout)

        # Details
        test_details_groupbox = QGroupBox("DETAILS")
        test_details_groupbox.setMaximumWidth(450)
        test_details_groupbox.setProperty("class", "left_panel_gb")
        f_test_details_layout = QFormLayout(test_details_groupbox)
        f_test_details_layout.addRow("Group:", self.group_label)
        f_test_details_layout.addRow("Model:", self.model_label)
        f_test_details_layout.addRow("Customer:", self.customer_label)
        f_test_details_layout.addRow("Input Type:", self.input_type_label)

        # Left Panel
        v_left_panel_layout = QVBoxLayout()
        v_left_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        v_left_panel_layout.addWidget(test_setup_groupbox)
        v_left_panel_layout.addWidget(test_info_groupbox)
        v_left_panel_layout.addWidget(test_details_groupbox)

        # Right Panel
        g_right_panel_layout = QGridLayout()
        g_right_panel_layout.setSpacing(20)
        g_right_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        columns = 2
        for i, channel in enumerate(self.test_controller.channel_list):
            g_right_panel_layout.addWidget(channel, i // columns, i % columns)

        # Main Layout
        h_main_layout = QHBoxLayout()
        h_main_layout.addLayout(v_left_panel_layout)
        h_main_layout.addLayout(g_right_panel_layout)

        return h_main_layout
