import time

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCloseEvent, QIcon, QIntValidator
from PySide6.QtWidgets import QWidget, QLineEdit, QComboBox, QGroupBox, QHBoxLayout, QFrame, QPushButton, QListWidget, \
    QVBoxLayout, QFormLayout, QLabel, QListWidgetItem

from controllers.test_file_controller import TestFileController
from views.custom_dialogs_view import ChannelSetupDialog, ParamsSetupDialog


def gen_id() -> int:
    return int(time.time() * 1000)


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


def get_selected_item_id(list_widget: QListWidget) -> int | None:
    item = list_widget.currentItem()
    if item:
        return item.data(Qt.ItemDataRole.UserRole)
    return None


class CreateTestWindow(QWidget):
    def __init__(self, parent: QWidget):
        super().__init__()
        self.parent_window = parent
        self.test_file_controller = TestFileController()
        self.setWindowTitle("Create Test File")

        # Components
        ## Fields
        self.group_field = QLineEdit()
        self.model_field = QLineEdit()
        self.customer_field = QLineEdit()
        self.input_type_field = QComboBox()
        self.input_type_field.addItems(["CC", "CA"])
        self.v1_input_field = QLineEdit()
        self.v2_input_field = QLineEdit()
        self.v3_input_field = QLineEdit()
        self.v1_input_field.setValidator(QIntValidator())
        self.v2_input_field.setValidator(QIntValidator())
        self.v3_input_field.setValidator(QIntValidator())
        ## Lists
        self.channel_list_widget = QListWidget()
        self.step_list_widget = QListWidget()
        self.param_list_widget = QListWidget()
        self.channel_list_widget.setProperty("class", "custom_list")
        self.step_list_widget.setProperty("class", "custom_list")
        self.param_list_widget.setProperty("class", "custom_list")
        ## Buttons
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
        self.remove_param_bt = custom_icon_button("minus.svg")

        # Signals
        self.save_data_bt.clicked.connect(self.save)
        self.clear_data_bt.clicked.connect(self.show_data)  # Teste
        self.add_channel_bt.clicked.connect(self.__show_channel_setup_dialog)
        self.edit_channel_bt.clicked.connect(lambda: self.__show_channel_setup_dialog(True))
        self.edit_param_bt.clicked.connect(lambda: self.__show_param_setup_dialog(True))
        self.clone_param_bt.clicked.connect(self.__clone_param)
        self.remove_channel_bt.clicked.connect(self.__remove_channel)
        self.remove_param_bt.clicked.connect(self.__remove_param)
        self.add_param_bt.clicked.connect(self.__show_param_setup_dialog)

        # Layout
        self.setLayout(self.__setup_layout())

    def save(self):
        self.test_file_controller.test_data.group = self.group_field.text()
        self.test_file_controller.test_data.model = self.model_field.text()
        self.test_file_controller.test_data.customer = self.customer_field.text()
        self.test_file_controller.test_data.input_type = self.input_type_field.currentText()
        self.test_file_controller.input_sources = [self.v1_input_field.text(), self.v2_input_field.text(),
                                                   self.v3_input_field.text()]

    # Teste
    def show_data(self):
        self.test_file_controller.show_data()

    def __show_param_setup_dialog(self, edit: bool = False):
        if edit:
            param_id = get_selected_item_id(self.param_list_widget)
            if param_id:
                param = self.test_file_controller.get_param(param_id)
                dialog = ParamsSetupDialog(param, self)
                if dialog.exec():
                    param.update(dialog.get_values())
                    self.__update_params_list()
        else:
            dialog = ParamsSetupDialog(None, self)
            if dialog.exec():
                self.test_file_controller.add_param(dialog.get_values())
                self.__update_params_list()

    def __show_channel_setup_dialog(self, edit: bool = False):
        channels = self.test_file_controller.get_available_channels()
        if edit:
            channel_id = get_selected_item_id(self.channel_list_widget)
            if channel_id:
                label = self.test_file_controller.active_channels.get(channel_id)
                dialog = ChannelSetupDialog(channels, (channel_id, label), self)
            else:
                return
        else:
            dialog = ChannelSetupDialog(channels, None, self)

        if dialog.exec():
            self.test_file_controller.active_channels.update(**dialog.get_values())
            self.__update_channels_list()

    def __clone_param(self):
        param_id = get_selected_item_id(self.param_list_widget)
        if param_id:
            self.test_file_controller.clone_param(param_id)
            self.__update_params_list()

    def __remove_param(self):
        pass  # TODO: Implementar apos STEPS, verificar se alguma step usa o parametro antes de remover

    def __remove_channel(self):
        if not self.step_list_widget.count() == 0:  # TODO: Invertido, corrigir apos implementar STEPS
            print("STEPS")
        else:
            channel_id = get_selected_item_id(self.channel_list_widget)
            if channel_id:
                self.test_file_controller.remove_channel(channel_id)
                self.__update_channels_list()

    def __update_channels_list(self):
        self.channel_list_widget.clear()
        for channel_id, label in self.test_file_controller.active_channels.items():
            item = QListWidgetItem(f"{channel_id} : {label}")
            item.setData(Qt.ItemDataRole.UserRole, channel_id)
            self.channel_list_widget.addItem(item)

    def __update_params_list(self):
        self.param_list_widget.clear()
        for param in self.test_file_controller.params:
            item = QListWidgetItem(
                f"{param['tag']} | {param['va']}V | {param['vb']}V | {param['ia']}A | {param['ib']}A ")
            item.setData(Qt.ItemDataRole.UserRole, param['id'])
            self.param_list_widget.addItem(item)

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
