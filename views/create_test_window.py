from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCloseEvent, QIcon
from PySide6.QtWidgets import QWidget, QLineEdit, QComboBox, QGroupBox, QHBoxLayout, QFrame, QPushButton, QListWidget, \
    QVBoxLayout, QFormLayout, QLabel


def custom_separator(vertical: bool = False) -> QFrame:
    separator = QFrame()
    separator.setFrameShape(QFrame.Shape.VLine if vertical else QFrame.Shape.HLine)
    separator.setFrameShadow(QFrame.Shadow.Plain)
    separator.setLineWidth(1)
    return separator


def custom_icon_button(icon: str, text: str = "", size: tuple[int, int] = (20, 20)) -> QPushButton:
    button = QPushButton(text=text, icon=QIcon(f"assets/icons/{icon}"))
    width, height = size
    button.setIconSize(QSize(width, height))
    return button


def custom_groupbox(title: str, max_width: int | None = None) -> QGroupBox:
    groupbox = QGroupBox(title)
    groupbox.setProperty("class", "test_file_form_gb")
    if max_width:
        groupbox.setMaximumWidth(max_width)

    return groupbox


class CreateTestWindow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__()
        self.parent_window = parent
        self.setWindowTitle("Create Test File")

        # Components
        ##Fields
        self.group_field = QLineEdit()
        self.model_field = QLineEdit()
        self.customer_field = QLineEdit()
        self.input_type_field = QComboBox()
        self.input_type_field.addItems(["CC", "CA"])
        self.v1_input_field = QLineEdit()
        self.v2_input_field = QLineEdit()
        self.v3_input_field = QLineEdit()
        ## Lists
        self.channel_list_widget = QListWidget()
        self.step_list_widget = QListWidget()
        self.param_list_widget = QListWidget()
        ##Buttons
        self.save_data_bt = custom_icon_button("save.svg", " SAVE")
        self.clear_data_bt = custom_icon_button("delete.svg", " CLEAR")
        self.add_channel_bt = custom_icon_button("add.svg")
        self.remove_channel_bt = custom_icon_button("minus.svg")
        self.edit_channel_bt = custom_icon_button("edit.svg")
        self.add_step_bt = custom_icon_button("add.svg")
        self.edit_step_bt = custom_icon_button("edit.svg")
        self.clone_step_bt = custom_icon_button("copy.svg")
        self.move_step_bt = custom_icon_button("swap.svg")
        self.show_step_bt = custom_icon_button("eye.svg")
        self.remove_step_bt = custom_icon_button("minus.svg")
        self.add_param_bt = custom_icon_button("add.svg")
        self.edit_param_bt = custom_icon_button("edit.svg")
        self.clone_param_bt = custom_icon_button("copy.svg")
        self.show_param_bt = custom_icon_button("eye.svg")
        self.remove_param_bt = custom_icon_button("minus.svg")

        # Layout
        self.setLayout(self.__setup_layout())

    def __setup_layout(self) -> QHBoxLayout:
        h_main_layout = QHBoxLayout()

        test_details_groupbox = custom_groupbox("Test Details", 400)
        steps_groupbox = custom_groupbox("Steps")
        params_groupbox = custom_groupbox("Parameters", 400)

        # Test Details
        f_test_details_container_layout = QFormLayout(test_details_groupbox)
        ## File Actions
        h_actions_layout = QHBoxLayout()
        h_actions_layout.addWidget(self.save_data_bt)
        h_actions_layout.addWidget(self.clear_data_bt)
        ## Inputs
        h_inputs_layout = QHBoxLayout()
        h_inputs_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        h_inputs_layout.addWidget(QLabel("V1"))
        h_inputs_layout.addWidget(self.v1_input_field)
        h_inputs_layout.addWidget(QLabel(" V2"))
        h_inputs_layout.addWidget(self.v2_input_field)
        h_inputs_layout.addWidget(QLabel(" V3"))
        h_inputs_layout.addWidget(self.v3_input_field)
        ## Channel Actions
        h_channel_actions_layout = QHBoxLayout()
        h_channel_actions_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        h_channel_actions_layout.addWidget(self.add_channel_bt)
        h_channel_actions_layout.addWidget(self.edit_channel_bt)
        h_channel_actions_layout.addWidget(self.remove_channel_bt)

        f_test_details_container_layout.addRow(h_actions_layout)
        f_test_details_container_layout.addRow(custom_separator())
        f_test_details_container_layout.addRow("Group:", self.group_field)
        f_test_details_container_layout.addRow("Model:", self.model_field)
        f_test_details_container_layout.addRow("Customer:", self.customer_field)
        f_test_details_container_layout.addRow("Input Type:", self.input_type_field)
        f_test_details_container_layout.addRow("Inputs:", h_inputs_layout)
        f_test_details_container_layout.addRow(custom_separator())
        f_test_details_container_layout.addRow("Channels", h_channel_actions_layout)
        f_test_details_container_layout.addRow(self.channel_list_widget)

        # Steps
        v_steps_container_layout = QVBoxLayout(steps_groupbox)
        ## Step Actions
        h_step_actions_layout = QHBoxLayout()
        h_step_actions_layout.addWidget(self.add_step_bt)
        h_step_actions_layout.addWidget(self.show_step_bt)
        h_step_actions_layout.addWidget(self.edit_step_bt)
        h_step_actions_layout.addWidget(self.move_step_bt)
        h_step_actions_layout.addWidget(self.clone_step_bt)
        h_step_actions_layout.addWidget(self.remove_step_bt)

        v_steps_container_layout.addLayout(h_step_actions_layout)
        v_steps_container_layout.addWidget(self.step_list_widget)

        # Params
        v_params_container_layout = QVBoxLayout(params_groupbox)
        ## Param Actions
        h_param_actions_layout = QHBoxLayout()
        h_param_actions_layout.addWidget(self.add_param_bt)
        h_param_actions_layout.addWidget(self.show_param_bt)
        h_param_actions_layout.addWidget(self.edit_param_bt)
        h_param_actions_layout.addWidget(self.clone_param_bt)
        h_param_actions_layout.addWidget(self.remove_param_bt)

        v_params_container_layout.addLayout(h_param_actions_layout)
        v_params_container_layout.addWidget(self.param_list_widget)

        # Main
        h_main_layout.addWidget(test_details_groupbox)
        h_main_layout.addWidget(steps_groupbox)
        h_main_layout.addWidget(params_groupbox)

        return h_main_layout

    def closeEvent(self, event: QCloseEvent) -> None:
        self.parent_window.show()
        event.accept()
