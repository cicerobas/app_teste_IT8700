from PySide6.QtCore import Qt, QSize, Slot
from PySide6.QtGui import QIntValidator, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLineEdit, QFormLayout, QPushButton, \
    QGridLayout, QLabel

from controllers.test_controller import TestController, TestState
from models.test_file_model import TestData
from views.channel_monitor_view import ChannelMonitorView

ICON_SIZE = QSize(20, 20)


class TestRunTabView(QWidget):
    def __init__(self, test_data: TestData, test_controller: TestController):
        super().__init__()
        self.test_data: TestData = test_data
        self.test_controller = test_controller

        # Components
        self.serial_number_field = QLineEdit()
        self.serial_number_field.setValidator(QIntValidator(0, 99999999, self))
        self.tester_id_field = QLineEdit()
        self.run_button = QPushButton(icon=QIcon('assets/icons/play.svg'), text=" RUN", parent=self)
        self.stop_button = QPushButton(icon=QIcon('assets/icons/stop.svg'), text=" STOP", parent=self)
        self.run_button.setIconSize(ICON_SIZE)
        self.stop_button.setIconSize(ICON_SIZE)
        self.current_state_label = QLabel("STATE: ")
        self.current_step_label = QLabel("STEP: ")
        self.timer_label = QLabel("0.0s")
        self.steps_progress_label = QLabel(f"0/{len(self.test_data.steps)}")

        # Signals
        self.run_button.clicked.connect(self.test_controller.start_test_sequence)
        self.stop_button.clicked.connect(self.test_controller.cancel_test_sequence)
        self.serial_number_field.textChanged.connect(self.__set_serial_number)
        self.test_controller.state_changed.connect(self.__update_status_label)
        self.test_controller.serial_number_updated.connect(self.__update_serial_number_field)
        self.test_controller.current_step_changed.connect(self.__set_step_info)
        self.test_controller.delay_manager.remaining_time_changed.connect(self.__update_timer)

        for channel_id in self.test_data.channels.keys():
            channel_monitor = ChannelMonitorView(channel_id)
            channel_monitor.setProperty("class", "channel_monitor")
            self.test_controller.channel_list.append(channel_monitor)

        self.setLayout(self.__setup_layout())

    @Slot(int)
    def __update_timer(self, remaining_time: int):
        self.timer_label.setText(f"{remaining_time / 1000}s")

    @Slot(str, float, int)
    def __set_step_info(self, description: str, duration: float, index: int):
        self.current_step_label.setText(f"STEP: {description}")
        self.timer_label.setText(f"{duration}s")
        self.steps_progress_label.setText(f"{index + 1}/{len(self.test_data.steps)}")

    @Slot(str)
    def __set_serial_number(self, value):
        self.test_controller.serial_number = value.zfill(8)

    @Slot(str)
    def __update_serial_number_field(self, value):
        self.serial_number_field.setText(value)

    @Slot(str)
    def __update_status_label(self, value):
        self.current_state_label.setText(f"STATE: {value}")
        self.__update_fields_state()

    def __update_fields_state(self):
        state = self.test_controller.state
        if state in [TestState.RUNNING, TestState.PAUSED]:
            self.serial_number_field.setReadOnly(True)
            self.tester_id_field.setReadOnly(True)
            self.run_button.setIcon(
                QIcon('assets/icons/pause.svg') if state is TestState.RUNNING else QIcon('assets/icons/play.svg'))
            self.run_button.setText(" PAUSE" if state is TestState.RUNNING else " CONTINUE")
            self.run_button.clicked.disconnect()
            self.run_button.clicked.connect(self.test_controller.toggle_test_pause_state)
        else:
            self.serial_number_field.setReadOnly(False)
            self.tester_id_field.setReadOnly(False)
            self.run_button.setIcon(QIcon('assets/icons/play.svg'))
            self.run_button.setText(" RUN")
            self.run_button.clicked.disconnect()
            self.run_button.clicked.connect(self.test_controller.start_test_sequence)

    def __setup_layout(self) -> QHBoxLayout:

        # ACTIONS
        action_buttons = QWidget()
        action_buttons.setFixedHeight(70)
        h_buttons_layout = QHBoxLayout()
        h_buttons_layout.addWidget(self.run_button)
        h_buttons_layout.addWidget(self.stop_button)
        action_buttons.setLayout(h_buttons_layout)

        # SETUP
        test_setup_groupbox = QGroupBox("SETUP")
        test_setup_groupbox.setProperty("class", "left_panel_gb")
        test_setup_groupbox.setFixedWidth(350)
        f_test_setup_layout = QFormLayout()
        f_test_setup_layout.addRow("Serial Nº : ", self.serial_number_field)
        f_test_setup_layout.addRow("Tester: ", self.tester_id_field)
        f_test_setup_layout.addRow(action_buttons)
        test_setup_groupbox.setLayout(f_test_setup_layout)

        # INFO
        test_info_groupbox = QGroupBox("INFO")
        test_info_groupbox.setProperty("class", "left_panel_gb")
        v_test_info_layout = QVBoxLayout()
        h_timer_progress_layout = QHBoxLayout()
        h_timer_progress_layout.addWidget(self.steps_progress_label)
        h_timer_progress_layout.addWidget(self.timer_label)
        v_test_info_layout.addWidget(self.current_state_label)
        v_test_info_layout.addWidget(self.current_step_label)
        v_test_info_layout.addLayout(h_timer_progress_layout)
        test_info_groupbox.setLayout(v_test_info_layout)

        # LEFT PANEL
        v_left_panel_layout = QVBoxLayout()
        v_left_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        v_left_panel_layout.addWidget(test_setup_groupbox)
        v_left_panel_layout.addWidget(test_info_groupbox)

        # RIGHT PANEL
        g_right_panel_layout = QGridLayout()
        g_right_panel_layout.setSpacing(20)
        g_right_panel_layout.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight)
        column = 2
        for i, channel in enumerate(self.test_controller.channel_list):
            g_right_panel_layout.addWidget(channel, i // column, i % column)

        # MAIN LAYOUT
        h_main_layout = QHBoxLayout()
        h_main_layout.addLayout(v_left_panel_layout)
        h_main_layout.addLayout(g_right_panel_layout)
        return h_main_layout
