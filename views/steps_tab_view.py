from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QFormLayout

from models.test_file_model import Step


class StepsTabView(QWidget):
    def __init__(self, steps: list[Step]):
        super().__init__()
        self.steps: list[Step] = steps

        self.step_list_view = QListWidget()

        for step in self.steps:
            self.step_list_view.addItem(f"{step.description}")

        h_main_layout = QHBoxLayout()
        h_main_layout.addWidget(self.step_list_view)

        self.setLayout(h_main_layout)
