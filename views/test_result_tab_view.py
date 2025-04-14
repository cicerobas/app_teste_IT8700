from PySide6.QtCore import Slot
from PySide6.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout

from controllers.test_controller import TestController


class TestResultTabView(QWidget):
    def __init__(self, test_controller: TestController):
        super().__init__()
        self.test_controller = test_controller
        self.text_view = QPlainTextEdit()
        self.text_view.setReadOnly(True)

        # Signals
        self.test_controller.result_file_updated.connect(self.__update_text)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_view)

    @Slot(str)
    def __update_text(self, text: str):
        self.text_view.setPlainText(text)
