from datetime import datetime
from enum import Enum
from typing import Optional

import yaml
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGridLayout, QFileDialog, QMessageBox

from models.test_file_model import TestData
from utils.config_manager import ConfigManager
from utils.constants import TEST_FILES_DIR
from utils.window_utils import center_window
from views.configs_window import ConfigWindow
from views.create_test_window import CreateTestWindow
from views.custom_dialogs_view import PasswordDialog
from views.test_window import TestWindow


class WindowOption(Enum):
    START = 0
    CREATE = 1
    EDIT = 2
    SETTINGS = 3


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

        # Components
        ## Logo
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("assets/logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setFixedSize(QSize(300, 200))
        ## Buttons
        self.start_button = QPushButton("START")
        self.create_button = QPushButton("CREATE")
        self.edit_button = QPushButton("EDIT")
        self.settings_button = QPushButton("SETTINGS")

        # Signals
        self.start_button.clicked.connect(lambda: self._show_window(WindowOption.START))
        self.create_button.clicked.connect(lambda: self._show_window(WindowOption.CREATE))
        self.edit_button.clicked.connect(lambda: self._show_window(WindowOption.EDIT))
        self.settings_button.clicked.connect(lambda: self._show_window(WindowOption.SETTINGS))

        self.setLayout(self._setup_layout())

    def _setup_layout(self) -> QVBoxLayout:
        # Buttons
        g_buttons_layout = QGridLayout()
        g_buttons_layout.addWidget(self.create_button, 1, 0, 1, 1)
        g_buttons_layout.addWidget(self.start_button, 0, 0, 1, 2)
        g_buttons_layout.addWidget(self.edit_button, 1, 1, 1, 1)
        g_buttons_layout.addWidget(self.settings_button, 2, 0, 1, 2)

        # Main Layout
        v_main_layout = QVBoxLayout()
        v_main_layout.setAlignment(
            Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop
        )
        v_main_layout.addWidget(self.logo)
        v_main_layout.addSpacing(30)
        v_main_layout.addLayout(g_buttons_layout)
        return v_main_layout

    def _show_file_load_dialog(self) -> Optional[str]:
        """Shows a file picker to load a .yaml formatted test file."""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Test File...",
            self.config.get(TEST_FILES_DIR),
            "YAML Files (*.yaml)",
        )
        if file_path and file_path.endswith(".yaml"):
            return file_path
        return None

    def _show_window(self, window_option: WindowOption) -> None:
        """Configures and displays the selected window."""
        match window_option:
            case WindowOption.START:
                file_path = self._show_file_load_dialog()
                if file_path:
                    with open(file_path, "r", encoding="utf-8") as file:
                        data = yaml.safe_load(file)
                    test_data = TestData(**data)
                    self.hide()
                    self.test_window = TestWindow(test_data, self)
                    self.test_window.showMaximized()
            case WindowOption.CREATE:
                if self._request_password():
                    self.hide()
                    self.create_test_window = CreateTestWindow(self)
                    self.create_test_window.showMaximized()
            case WindowOption.EDIT:
                if self._request_password():
                    file_path = self._show_file_load_dialog()
                    if file_path:
                        self.hide()
                        self.create_test_window = CreateTestWindow(self, True, file_path)
                        self.create_test_window.showMaximized()
            case WindowOption.SETTINGS:
                if self._request_password():
                    self.hide()
                    self.config_window.show()

    def _request_password(self) -> bool:
        """Compares the typed password with the pattern."""
        key = datetime.now().strftime("%d%m")
        dialog = PasswordDialog(self)
        if dialog.exec():
            password = dialog.get_password()
            if password == key:
                return True
            QMessageBox.warning(self, "Authentication Failed", "Wrong Password!")
        return False
