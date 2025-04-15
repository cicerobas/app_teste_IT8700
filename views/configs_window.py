from PySide6.QtCore import Qt
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QWidget, QLineEdit, QSpinBox, QVBoxLayout, QGroupBox, QLabel, QPushButton, QGridLayout, \
    QComboBox

from controllers.arduino_controller import ArduinoController
from utils.config_manager import ConfigManager
from utils.constants import *
from utils.window_utils import center_window


class ConfigWindow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__()
        self.parent_window = parent
        self.config = ConfigManager()
        self.arduino_controller = ArduinoController()
        self.setWindowTitle("Settings")
        self.setFixedWidth(500)
        center_window(self)

        self.changes = {}
        self.pins_setup = [(1, "CA"), (2, "CA"), (3, "CA"), (1, "CC"), (2, "CC"), (3, "CC")]

        # Components
        self.test_files_dir_field = QLineEdit(self.config.get(TEST_FILES_DIR))
        self.sat_resource_path_field = QLineEdit(self.config.get(SAT_RESOURCE_PATH))
        self.arduino_resource_path_field = QLineEdit(self.config.get(ARDUINO_RESOURCE_PATH))
        self.arduino_serial_port_field = QLineEdit(self.config.get(ARDUINO_SERIAL_PORT))
        self.sat_baud_rate_field = QSpinBox()
        self.arduino_baud_rate_field = QSpinBox()
        self.sat_baud_rate_field.setRange(0, 115200)
        self.arduino_baud_rate_field.setRange(0, 115200)
        self.sat_baud_rate_field.setValue(self.config.get(SAT_BAUD_RATE))
        self.arduino_baud_rate_field.setValue(self.config.get(ARDUINO_BAUD_RATE))
        self.apply_changes_button = QPushButton(text="Apply", icon=QIcon("assets/icons/check.svg"))
        self.apply_changes_button.setEnabled(False)
        self.arduino_pins_combobox = QComboBox()
        self.arduino_pins_combobox.addItems(
            ["Pino 4: CA1", "Pino 5: CA2", "Pino 6: CA3", "Pino 7: CC1", "Pino 8: CC2", "Pino 9: CC3",
             "Pino 10: Buzzer"])
        self.test_pin_button = QPushButton(text="Test Pin", icon=QIcon("assets/icons/switch.svg"))

        # Signals
        self.test_files_dir_field.textChanged.connect(lambda value: self.set_changed_fields(TEST_FILES_DIR, value))
        self.sat_resource_path_field.textChanged.connect(
            lambda value: self.set_changed_fields(SAT_RESOURCE_PATH, value))
        self.arduino_resource_path_field.textChanged.connect(
            lambda value: self.set_changed_fields(ARDUINO_RESOURCE_PATH, value))
        self.arduino_serial_port_field.textChanged.connect(
            lambda value: self.set_changed_fields(ARDUINO_SERIAL_PORT, value))
        self.sat_baud_rate_field.valueChanged.connect(lambda value: self.set_changed_fields(SAT_BAUD_RATE, value))
        self.arduino_baud_rate_field.valueChanged.connect(
            lambda value: self.set_changed_fields(ARDUINO_BAUD_RATE, value))
        self.apply_changes_button.clicked.connect(self.apply_changes)
        self.test_pin_button.clicked.connect(self.__test_arduino_pin)

        self.setLayout(self.__setup_layout())

    def __setup_layout(self) -> QVBoxLayout:
        global_config_gb = QGroupBox("Global")
        sat_config_gb = QGroupBox("SAT")
        arduino_config_gb = QGroupBox("Arduino")

        v_global_config_layout = QVBoxLayout()
        v_global_config_layout.addWidget(QLabel("Test Files Directory:"))
        v_global_config_layout.addWidget(self.test_files_dir_field)
        global_config_gb.setLayout(v_global_config_layout)

        v_sat_config_layout = QVBoxLayout()
        v_sat_config_layout.addWidget(QLabel("Resource Path:"))
        v_sat_config_layout.addWidget(self.sat_resource_path_field)
        v_sat_config_layout.addWidget(QLabel("Baud Rate:"))
        v_sat_config_layout.addWidget(self.sat_baud_rate_field)
        sat_config_gb.setLayout(v_sat_config_layout)

        g_arduino_config_layout = QGridLayout(arduino_config_gb)
        g_arduino_config_layout.addWidget(QLabel("Resource Path:"), 0, 0, 1, 6)
        g_arduino_config_layout.addWidget(self.arduino_resource_path_field, 1, 0, 1, 6)
        g_arduino_config_layout.addWidget(QLabel("Serial Port:"), 2, 0, 1, 3)
        g_arduino_config_layout.addWidget(self.arduino_serial_port_field, 3, 0, 1, 3)
        g_arduino_config_layout.addWidget(QLabel("Baud Rate:"), 2, 3, 1, 3)
        g_arduino_config_layout.addWidget(self.arduino_baud_rate_field, 3, 3, 1, 3)
        g_arduino_config_layout.addWidget(QLabel("Test Arduino Pins:"), 4, 0, 1, 6)
        g_arduino_config_layout.addWidget(self.arduino_pins_combobox, 5, 0, 1, 3)
        g_arduino_config_layout.addWidget(self.test_pin_button, 5, 3, 1, 3)

        v_main_layout = QVBoxLayout()
        v_main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        v_main_layout.addWidget(global_config_gb)
        v_main_layout.addWidget(sat_config_gb)
        v_main_layout.addWidget(arduino_config_gb)
        v_main_layout.addStretch(1)
        v_main_layout.addWidget(self.apply_changes_button, alignment=Qt.AlignmentFlag.AlignRight)

        return v_main_layout

    def __test_arduino_pin(self):
        selected_index = self.arduino_pins_combobox.currentIndex()
        if selected_index == 6:
            self.arduino_controller.buzzer()
        else:
            input_source, input_type = self.pins_setup[selected_index]
            self.arduino_controller.set_input_source(input_source, input_type)

    def set_changed_fields(self, key: str, value):
        self.changes.update({key: value})
        self.apply_changes_button.setEnabled(True)

    def apply_changes(self):
        for key, value in self.changes.items():
            self.config.set(key, value)
        self.apply_changes_button.setEnabled(False)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.arduino_controller.setup_active_pin(True)
        self.changes.clear()
        self.parent_window.show()
        event.accept()
