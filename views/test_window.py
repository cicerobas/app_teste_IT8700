from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCloseEvent, QPixmap
from PySide6.QtWidgets import QWidget, QLabel, QVBoxLayout, QHBoxLayout, QTabWidget

from models.test_file_model import TestData
from views.steps_tab_view import StepsTabView


class TestWindow(QWidget):
    def __init__(self, test_data:TestData, parent: QWidget):
        super().__init__()
        self.test_data = test_data
        self.parent_window = parent

        self.setWindowTitle("CEBRA IT8700")

        # LOGO
        self.logo = QLabel()
        self.logo.setPixmap(QPixmap("assets/logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setFixedSize(QSize(150, 70))

        self.tabs = QTabWidget()
        self.test_run_tab = QWidget()
        self.test_steps_tab = StepsTabView(self.test_data.steps)

        self.tabs.addTab(self.test_run_tab, "RUN")
        self.tabs.addTab(self.test_steps_tab, "STEPS")

        v_main_layout = QVBoxLayout()
        v_main_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        h_header_layout = QHBoxLayout()
        h_header_layout.addWidget(self.logo, alignment=Qt.AlignmentFlag.AlignLeft)

        v_main_layout.addLayout(h_header_layout)
        v_main_layout.addSpacing(10)
        v_main_layout.addWidget(self.tabs)
        self.setLayout(v_main_layout)

    def closeEvent(self, event: QCloseEvent) -> None:
        self.parent_window.show()
        event.accept()