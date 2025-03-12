from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIntValidator, QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QVBoxLayout, QGroupBox, QLineEdit, QFormLayout, QPushButton, QLabel, \
    QGridLayout

from models.test_file_model import TestData

class ChannelMonitorView(QGroupBox):
    def __init__(self, channel_id:int):
        super().__init__()
        self.channel_id = channel_id
        self.setTitle(f"Channel {self.channel_id}")
        self.setFixedSize(QSize(250, 150))

        self.voltage_label = QLabel("0 V")
        self.current_label = QLabel("0 A")
        self.power_label = QLabel("0 W")

        g_monitor_layout = QGridLayout()
        g_monitor_layout.addWidget(self.voltage_label, 0, 0, 2, 1)
        g_monitor_layout.addWidget(self.current_label, 0, 1, 1, 1)
        g_monitor_layout.addWidget(self.power_label, 1, 1, 1, 1)

        self.setLayout(g_monitor_layout)

    def set_voltage(self, voltage: float):
        self.voltage_label.setText(f"{'%.2f' % voltage} V")
        self.update_power()

    def set_current(self, current: float):
        self.current_label.setText(f"{'%.2f' % current} A")
        self.update_power()

    def update_power(self):
        power = float(self.voltage_label.text()) * float(self.current_label.text())
        self.power_label.setText(f"{'%.2f' % power} W")

class TestRunTabView(QWidget):
    def __init__(self, test_data: TestData):
        super().__init__()
        self.test_data: TestData = test_data
        self.channel_list:list[ChannelMonitorView] = []

        test_setup_groupbox = QGroupBox("SETUP")
        test_setup_groupbox.setMaximumWidth(300)
        self.serial_number_field = QLineEdit()
        self.serial_number_field.setValidator(QIntValidator(0, 99999999, self))
        self.tester_id_field = QLineEdit()
        f_test_setup_layout = QFormLayout()
        f_test_setup_layout.addRow("Serial Nº : ", self.serial_number_field)
        f_test_setup_layout.addRow("Tester: ", self.tester_id_field)
        test_setup_groupbox.setLayout(f_test_setup_layout)

        # ACTIONS
        action_buttons_groupbox = QGroupBox()
        action_buttons_groupbox.setFixedHeight(50)
        self.start_button = QPushButton(icon=QIcon('assets/icons/play_arrow_24dp_000000.svg'), text="RUN", parent=self)
        self.pause_button = QPushButton("PAUSE")
        self.stop_button = QPushButton(icon=QIcon('assets/icons/stop_24dp_000000.svg'), text="STOP", parent=self)
        h_buttons_layout = QHBoxLayout()
        h_buttons_layout.addWidget(self.start_button)
        # h_buttons_layout.addWidget(self.pause_button)
        h_buttons_layout.addWidget(self.stop_button)
        action_buttons_groupbox.setLayout(h_buttons_layout)

        # INFO
        test_info_groupbox = QGroupBox("INFO")
        v_test_info_layout = QVBoxLayout()
        h_timer_progress_layout = QHBoxLayout()
        self.current_status_label = QLabel("STATUS Placeholder")
        self.current_step_label = QLabel("STEP Placeholder")
        self.timer_label = QLabel("0.0s")
        self.steps_progress_label = QLabel("1/12")
        h_timer_progress_layout.addWidget(self.steps_progress_label)
        h_timer_progress_layout.addWidget(self.timer_label)
        v_test_info_layout.addWidget(self.current_status_label)
        v_test_info_layout.addWidget(self.current_step_label)
        v_test_info_layout.addLayout(h_timer_progress_layout)
        test_info_groupbox.setLayout(v_test_info_layout)

        # LEFT PANEL
        v_left_panel_layout = QVBoxLayout()
        v_left_panel_layout.addWidget(test_setup_groupbox)
        v_left_panel_layout.addWidget(action_buttons_groupbox)
        v_left_panel_layout.addWidget(test_info_groupbox)

        # RIGHT PANEL
        v_right_panel_layout = QVBoxLayout()
        for channel_id in self.test_data.channels.keys():
            self.channel_list.append(ChannelMonitorView(channel_id))

        for channel in self.channel_list:
            v_right_panel_layout.addWidget(channel)

        # MAIN LAYOUT
        h_main_layout = QHBoxLayout()
        h_main_layout.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        h_main_layout.addLayout(v_left_panel_layout)
        h_main_layout.addLayout(v_right_panel_layout)
        self.setLayout(h_main_layout)
