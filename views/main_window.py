from datetime import datetime

import yaml
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGridLayout, QFileDialog

from models.test_file_model import TestData
from utils.config_manager import ConfigManager
from utils.constants import TEST_FILES_DIR
from utils.window_utils import center_window
from views.configs_window import ConfigWindow
from views.create_test_window import CreateTestWindow
from views.custom_dialogs_view import PasswordDialog
from views.test_window import TestWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

        self.setWindowTitle("CEBRA IT8700")
        self.setFixedSize(QSize(400, 400))
        center_window(self)

        self.config_window = ConfigWindow(self)
        self.create_test_window = None
        self.test_window = None

        # LOGO
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("assets/logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setFixedSize(QSize(300, 200))

        # BUTTONS
        self.start_button = QPushButton("START")
        self.create_button = QPushButton("CREATE")
        self.edit_button = QPushButton("EDIT")
        self.settings_button = QPushButton("SETTINGS")

        # BUTTONS LAYOUT
        self.g_buttons_layout = QGridLayout()
        self.g_buttons_layout.addWidget(self.start_button, 0, 0, 1, 2)
        self.g_buttons_layout.addWidget(self.create_button, 1, 0, 1, 1)
        self.g_buttons_layout.addWidget(self.edit_button, 1, 1, 1, 1)
        self.g_buttons_layout.addWidget(self.settings_button, 2, 0, 1, 2)

        # MAIN LAYOUT
        self.v_main_layout = QVBoxLayout()
        self.v_main_layout.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        self.v_main_layout.addWidget(self.logo)
        self.v_main_layout.addSpacing(30)
        self.v_main_layout.addLayout(self.g_buttons_layout)

        self.setLayout(self.v_main_layout)
        self.connect_signals()

    def connect_signals(self):
        self.start_button.clicked.connect(lambda: self.show_window(0))
        self.create_button.clicked.connect(lambda: self.show_window(1))
        self.edit_button.clicked.connect(lambda: self.show_window(2))
        self.settings_button.clicked.connect(lambda: self.show_window(3))

    def show_file_load_dialog(self) -> str | None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Test File...",
            self.config.get(TEST_FILES_DIR),
            "YAML Files (*.yaml)",
        )
        return file_path or None

    def show_window(self, window_id: int) -> None:
        match window_id:
            case 0:
                file_path = self.show_file_load_dialog()
                if file_path:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = yaml.safe_load(file)
                    test_data = TestData(**data)
                    self.hide()
                    self.test_window = TestWindow(test_data, self)
                    self.test_window.showMaximized()
            case 1:
                if self.__request_password():
                    self.hide()
                    self.create_test_window = CreateTestWindow(self)
                    self.create_test_window.showMaximized()
            case 2:
                if self.__request_password():
                    file_path = self.show_file_load_dialog()
                    if file_path:
                        self.hide()
                        self.create_test_window = CreateTestWindow(self, True, file_path)
                        self.create_test_window.showMaximized()
            case 3:
                if self.__request_password():
                    self.hide()
                    self.config_window.show()

    def __request_password(self) -> bool:
        key = datetime.now().strftime("%d%m")
        dialog = PasswordDialog(self)
        if dialog.exec():
            password = dialog.get_password()
            return password == key
        return False
