import yaml
from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QPushButton, QGridLayout, QFileDialog

from utils.config_manager import ConfigManager
from utils.constants import TEST_FILES_DIR
from utils.window_utils import center_window
from views.configs_window import ConfigWindow


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.config = ConfigManager()

        self.setWindowTitle("CEBRA IT8700")
        self.setFixedSize(QSize(400, 400))
        center_window(self)

        self.config_window = ConfigWindow(self)
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
        self.settings_button.clicked.connect(lambda: self.show_window(3))

    def show_file_load_dialog(self) -> str | None:
        """
        Exibe um diálogo para carregar um arquivo de teste (.yaml).
        :return: Objeto referente ao arquivo carregado ou None.
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Open Test File...",
            self.config.get(TEST_FILES_DIR),
            "YAML Files (*.yaml)",
        )
        return file_path or None


    def show_window(self, window_id: int) -> None:
        """
        Esconde a janela principal e exibe a janela correspondente.\n
        * 0 -> TestViewWindow\n
        * 1 -> TestEditWindow (CREATE)\n
        * 2 -> TestEditWindow (UPDATE)
        * 3 -> ConfigWindow
        :param window_id: Identificador da janela a ser exibida.
        """
        match window_id:
            case 0:
                print("Janela A")
            case 3:
                self.hide()
                self.config_window.show()

