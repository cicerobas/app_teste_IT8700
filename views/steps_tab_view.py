from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QWidget, QHBoxLayout, QListWidget, QFormLayout, QListWidgetItem, QLabel, QGroupBox, \
    QPushButton, QScrollArea, QVBoxLayout

from controllers.test_controller import TestController
from models.test_file_model import Step, TestData
from utils.constants import STEP_TYPES_MAP


def custom_info_label(text: str = "") -> QLabel:
    label = QLabel(text)
    label.setProperty("class", "info_label")
    return label


class StepsTabView(QWidget):
    def __init__(self, test_data: TestData, test_controller: TestController):
        super().__init__()
        self.test_data: TestData = test_data
        self.test_controller = test_controller

        # Components
        self.step_list_view = QListWidget()
        self.step_list_view.setProperty("class", "custom_list")
        self.step_description_label = custom_info_label()
        self.step_type_label = custom_info_label()
        self.step_duration_label = custom_info_label()
        self.step_input_source_label = custom_info_label()
        self.f_channels_group_layout = QFormLayout()

        # Signals
        self.step_list_view.currentRowChanged.connect(self._setup_step_details)

        self.setLayout(self._setup_layout())

    def _setup_step_details(self) -> None:
        step = self.test_data.steps[self.step_list_view.currentIndex().row()]
        self.step_description_label.setText(step.description)

        step_type = STEP_TYPES_MAP.get(step.step_type)
        self.step_type_label.setText(step_type)
        self.step_duration_label.setText(f"{step.duration} s")
        self.step_input_source_label.setText(
            f"{self.test_data.input_sources[step.input_source]} V{self.test_data.input_type.lower()}")
        self._setup_channels_groupbox(step)

    def _setup_channels_groupbox(self, step: Step) -> None:
        self._clear_channels_group_layout()
        for channel, param in step.channel_params.items():
            params = next((param_item for param_item in self.test_data.params if param_item.id == param), None)
            self.f_channels_group_layout.addRow(f"Channel {channel}:",
                                                custom_info_label(f"{self.test_data.channels.get(channel)}"))
            match step.step_type:
                case 1:
                    self.f_channels_group_layout.addRow("Voltage Upper:", custom_info_label(f"{params.vb} V"))
                    self.f_channels_group_layout.addRow("Voltage Lower:", custom_info_label(f"{params.va} V"))
                    self.f_channels_group_layout.addRow("Static Load:", custom_info_label(f"{params.ia} A"))
                case 2:
                    self.f_channels_group_layout.addRow("Load Upper:", custom_info_label(f"{params.ib} A"))
                    self.f_channels_group_layout.addRow("Load Lower:", custom_info_label(f"{params.ia} A"))
                    self.f_channels_group_layout.addRow("Voltage Under:", custom_info_label(f"{params.va} V"))
                case 3:
                    self.f_channels_group_layout.addRow("Voltage Under:", custom_info_label(f"{params.va} V"))

            self.f_channels_group_layout.addRow(QLabel())

    def _clear_channels_group_layout(self) -> None:
        while self.f_channels_group_layout.count():
            item = self.f_channels_group_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def _set_custom_list_item(self, step: Step) -> None:
        """Creates a default step list item with a RUN button."""
        step_item = QListWidgetItem()
        step_item.setData(Qt.ItemDataRole.UserRole, step.id)
        step_item_widget = QWidget()
        run_step_button = QPushButton(" RUN")
        run_step_button.setIcon(QIcon('assets/icons/play.svg'))
        run_step_button.clicked.connect(lambda _: self.test_controller.setup_single_run(step.id))
        step_item_layout = QHBoxLayout(step_item_widget)
        step_item_layout.addWidget(QLabel(step.description))
        step_item_layout.addWidget(run_step_button, alignment=Qt.AlignmentFlag.AlignRight)
        step_item.setSizeHint(step_item_widget.sizeHint())
        self.step_list_view.addItem(step_item)
        self.step_list_view.setItemWidget(step_item, step_item_widget)

    def _setup_layout(self) -> QHBoxLayout:
        self.step_list_view.setMaximumWidth(450)
        for step in self.test_data.steps:
            self._set_custom_list_item(step)

        scroll_widget = QWidget()
        scroll_widget.setLayout(self.f_channels_group_layout)
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(scroll_widget)

        step_details_groupbox = QGroupBox("Details")
        step_details_groupbox.setProperty("class", "details_gb")

        step_channels_setup_groupbox = QGroupBox("Channels:")
        step_channels_setup_groupbox.setProperty("class", "details_gb")
        step_channels_setup_layout = QVBoxLayout(step_channels_setup_groupbox)
        step_channels_setup_layout.addWidget(scroll_area)

        f_details_layout = QFormLayout(step_details_groupbox)
        f_details_layout.addRow("Description: ", self.step_description_label)
        f_details_layout.addRow("Type: ", self.step_type_label)
        f_details_layout.addRow("Duration: ", self.step_duration_label)
        f_details_layout.addRow("Input Source: ", self.step_input_source_label)
        f_details_layout.addRow(step_channels_setup_groupbox)

        h_main_layout = QHBoxLayout()
        h_main_layout.addWidget(self.step_list_view)
        h_main_layout.addWidget(step_details_groupbox)

        return h_main_layout
