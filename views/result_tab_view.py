from PySide6.QtCore import Slot
from PySide6.QtGui import QFontDatabase
from PySide6.QtWidgets import QWidget, QPlainTextEdit, QVBoxLayout

from controllers.test_controller import TestController


class TestResultTabView(QWidget):
    def __init__(self, test_controller: TestController):
        super().__init__()
        self.test_controller = test_controller

        # Components
        self.text_view = QPlainTextEdit()
        self.text_view.setReadOnly(True)
        font = QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont)
        font.setPointSize(16)
        self.text_view.setFont(font)

        # Signals
        self.test_controller.result_file_updated.connect(self._update_text)

        # Layout
        layout = QVBoxLayout(self)
        layout.addWidget(self.text_view)

    @Slot(str)
    def _update_text(self, text: str) -> None:
        self.text_view.setPlainText(text)
