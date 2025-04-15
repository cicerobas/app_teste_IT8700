from PySide6.QtWidgets import QGroupBox, QLabel, QFormLayout, QWidget

from controllers.test_controller import TestController
from models.test_file_model import TestData


class DetailsTabView(QWidget):
    def __init__(self, test_data: TestData, test_controller: TestController):
        super().__init__()
        self.test_data: TestData = test_data
        self.test_controller = test_controller
        self.setMaximumWidth(400)

        # Components
        self.group_label = QLabel(self.test_data.group)
        self.model_label = QLabel(self.test_data.model)
        self.customer_label = QLabel(self.test_data.customer)
        self.input_type_label = QLabel(self.test_data.input_type)

        # layout
        layout = QFormLayout(self)
        layout.addRow("Group:", self.group_label)
        layout.addRow("Model:", self.model_label)
        layout.addRow("Customer:", self.customer_label)
        layout.addRow("Input Type:", self.input_type_label)
