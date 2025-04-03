from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIntValidator, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLineEdit, QFormLayout, QPushButton, \
    QGridLayout, QLabel

from controllers.test_controller import TestController
from models.test_file_model import TestData
from views.channel_monitor_view import ChannelMonitorView

ICON_SIZE = QSize(20,20)

class TestRunTabView(QWidget):
    def __init__(self, test_data: TestData, test_controller:TestController):
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
        self.current_status_label = QLabel("STATUS Placeholder")
        self.current_step_label = QLabel("STEP Placeholder")
        self.timer_label = QLabel("0.0s")
        self.steps_progress_label = QLabel("1/12")

        for channel_id in self.test_data.channels.keys():
            channel_monitor = ChannelMonitorView(channel_id)
            channel_monitor.setProperty("class", "channel_monitor")
            self.test_controller.channel_list.append(channel_monitor)

        self.setLayout(self.__setup_layout())

    def __setup_layout(self) -> QHBoxLayout:

        # ACTIONS
        action_buttons = QWidget()
        action_buttons.setFixedHeight(70)
        h_buttons_layout = QHBoxLayout()
        h_buttons_layout.addWidget(self.run_button)
        h_buttons_layout.addWidget(self.stop_button)
        action_buttons.setLayout(h_buttons_layout)

        #SETUP
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
        v_test_info_layout.addWidget(self.current_status_label)
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
