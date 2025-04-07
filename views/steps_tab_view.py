from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QFormLayout, QListWidgetItem, QLabel, QGroupBox, \
    QVBoxLayout, QPushButton

from controllers.test_controller import TestController
from models.test_file_model import Step, TestData


class StepsTabView(QWidget):
    def __init__(self, test_data: TestData, test_controller: TestController):
        super().__init__()
        self.test_data: TestData = test_data
        self.test_controller = test_controller

        self.step_list_view = QListWidget()
        self.step_list_view.setMaximumWidth(450)
        self.step_list_view.currentRowChanged.connect(self.setup_step_details)

        for step in self.test_data.steps:
            self.__setup_custom_list_item(step)

        self.step_description_label = QLabel()
        self.step_type_label = QLabel()
        self.step_duration_label = QLabel()
        self.step_input_source_label = QLabel()
        self.step_channels_setup_groupbox = QGroupBox("Channels:")
        self.v_channels_group_layout = QVBoxLayout()
        self.step_channels_setup_groupbox.setLayout(self.v_channels_group_layout)

        f_details_layout = QFormLayout()
        f_details_layout.addRow("Description: ", self.step_description_label)
        f_details_layout.addRow("Type: ", self.step_type_label)
        f_details_layout.addRow("Duration: ", self.step_duration_label)
        f_details_layout.addRow("Input Source: ", self.step_input_source_label)
        f_details_layout.addRow(self.step_channels_setup_groupbox)

        h_main_layout = QHBoxLayout()
        h_main_layout.addWidget(self.step_list_view)
        h_main_layout.addLayout(f_details_layout)

        self.setLayout(h_main_layout)

    def setup_step_details(self):
        step = self.test_data.steps[self.step_list_view.currentIndex().row()]
        self.step_description_label.setText(step.description)
        step_type = ""
        match step.step_type:
            case 1:
                step_type = "Direct Current"
            case 2:
                step_type = "Over current"
            case 3:
                step_type = "Automatic Short"
        self.step_type_label.setText(step_type)
        self.step_duration_label.setText(f"{step.duration} s")
        self.step_input_source_label.setText(
            f"{self.test_data.input_sources[step.input_source]} V{self.test_data.input_type.lower()}")
        self.setup_channels_groupbox(step)

    def setup_channels_groupbox(self, step: Step):
        self.clear_channels_group_layout()
        for channel, param in step.channel_params.items():
            params = next((param_item for param_item in self.test_data.params if param_item.id == param), None)
            self.v_channels_group_layout.addWidget(QLabel(f"Channel {channel}: {self.test_data.channels.get(channel)}"))
            match step.step_type:
                case 1:
                    self.v_channels_group_layout.addWidget(QLabel(f"Voltage Upper: {params.vb} V"))
                    self.v_channels_group_layout.addWidget(QLabel(f"Voltage Lower: {params.va} V"))
                    self.v_channels_group_layout.addWidget(QLabel(f"Static Load: {params.ia} A"))
                case 2:
                    self.v_channels_group_layout.addWidget(QLabel(f"Load Upper: {params.ib} A"))
                    self.v_channels_group_layout.addWidget(QLabel(f"Load Lower: {params.ia} A"))
                    self.v_channels_group_layout.addWidget(QLabel(f"Voltage Under: {params.va} V"))
                case 3:
                    self.v_channels_group_layout.addWidget(QLabel(f"Voltage Under: {params.va} V"))

            self.v_channels_group_layout.addSpacing(20)

    def clear_channels_group_layout(self):
        while self.v_channels_group_layout.count():
            item = self.v_channels_group_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def __setup_custom_list_item(self, step: Step):
        step_item = QListWidgetItem()
        step_item.setData(Qt.ItemDataRole.UserRole, step.id)
        step_item_widget = QWidget()
        run_step_button = QPushButton(" RUN")
        run_step_button.setIcon(QIcon('assets/icons/play.svg'))
        run_step_button.clicked.connect(lambda _: self.test_controller.setup_single_run(step.id))
        step_item_layout = QHBoxLayout()
        step_item_layout.addWidget(QLabel(step.description))
        step_item_layout.addWidget(run_step_button, alignment=Qt.AlignmentFlag.AlignRight)
        step_item_widget.setLayout(step_item_layout)
        step_item.setSizeHint(step_item_widget.sizeHint())
        self.step_list_view.addItem(step_item)
        self.step_list_view.setItemWidget(step_item, step_item_widget)
