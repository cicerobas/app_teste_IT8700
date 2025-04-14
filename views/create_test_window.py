from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QCloseEvent, QIcon, QIntValidator
from PySide6.QtWidgets import QWidget, QLineEdit, QComboBox, QGroupBox, QHBoxLayout, QFrame, QPushButton, QListWidget, \
    QVBoxLayout, QFormLayout, QLabel, QListWidgetItem, QMessageBox, QFileDialog, QTableWidget, QTableWidgetItem, \
    QAbstractItemView, QHeaderView

from controllers.test_file_controller import TestFileController
from utils.config_manager import ConfigManager
from utils.constants import TEST_FILES_DIR
from utils.window_utils import show_custom_dialog
from views.custom_dialogs_view import ChannelSetupDialog, ParamsSetupDialog, StepSetupDialog, StepPositionDialog


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


def get_selected_item_id(data_widget) -> int | None:
    if isinstance(data_widget, QListWidget):
        item = data_widget.currentItem()
        if item:
            return item.data(Qt.ItemDataRole.UserRole)
    elif isinstance(data_widget, QTableWidget):
        item = data_widget.item(data_widget.currentRow(), 0)
        if item:
            return item.data(Qt.ItemDataRole.UserRole)

    return None


class CreateTestWindow(QWidget):
    def __init__(self, parent: QWidget, is_editing: bool = False, editing_file_path: str = ""):
        super().__init__()
        self.parent_window = parent
        self.is_editing = is_editing
        self.editing_file_path = editing_file_path
        self.test_file_controller = TestFileController()
        self.config = ConfigManager()
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
        self.params_table = QTableWidget()
        self.__setup_params_table()

        self.channel_list_widget.setProperty("class", "custom_list")
        self.step_list_widget.setProperty("class", "custom_list")
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
        self.remove_step_bt = custom_icon_button("minus.svg")
        self.add_param_bt = custom_icon_button("add.svg")
        self.edit_param_bt = custom_icon_button("edit.svg")
        self.clone_param_bt = custom_icon_button("copy.svg")
        self.remove_param_bt = custom_icon_button("minus.svg")

        # Signals
        self.save_data_bt.clicked.connect(self.__save_test_data)
        self.clear_data_bt.clicked.connect(self.__clear_fields)
        self.add_channel_bt.clicked.connect(self.__show_channel_setup_dialog)
        self.add_step_bt.clicked.connect(self.__show_step_setup_dialog)
        self.edit_channel_bt.clicked.connect(lambda: self.__show_channel_setup_dialog(True))
        self.edit_param_bt.clicked.connect(lambda: self.__show_param_setup_dialog(True))
        self.edit_step_bt.clicked.connect(lambda: self.__show_step_setup_dialog(True))
        self.clone_param_bt.clicked.connect(self.__clone_param)
        self.clone_step_bt.clicked.connect(self.__clone_step)
        self.move_step_bt.clicked.connect(self.__move_step)
        self.remove_channel_bt.clicked.connect(self.__remove_channel)
        self.remove_param_bt.clicked.connect(self.__remove_param)
        self.remove_step_bt.clicked.connect(self.__remove_step)
        self.add_param_bt.clicked.connect(self.__show_param_setup_dialog)

        if self.is_editing:
            self.test_file_controller.load_file_data(self.editing_file_path)
            self.__set_editing_field_values()

        # Layout
        self.setLayout(self.__setup_layout())

    def __setup_params_table(self):
        self.params_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.params_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.params_table.setColumnCount(5)
        self.params_table.setHorizontalHeaderLabels(["Tag", "Va (V)", "Vb (V)", "Ia (A)", "Ib (A)"])
        self.params_table.verticalHeader().setVisible(False)
        self.params_table.setColumnWidth(0, 100)
        self.params_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        for col in range(1, self.params_table.columnCount()):
            self.params_table.horizontalHeader().setSectionResizeMode(col, QHeaderView.ResizeMode.Stretch)

    def __set_editing_field_values(self):
        self.group_field.setText(self.test_file_controller.test_data.group)
        self.model_field.setText(self.test_file_controller.test_data.model)
        self.customer_field.setText(self.test_file_controller.test_data.customer)
        self.input_type_field.setCurrentIndex(0 if self.test_file_controller.test_data.input_type == 'CC' else 1)
        self.v1_input_field.setText(str(self.test_file_controller.test_data.input_sources[0]))
        self.v2_input_field.setText(str(self.test_file_controller.test_data.input_sources[1]))
        self.v3_input_field.setText(str(self.test_file_controller.test_data.input_sources[2]))
        self.__update_channels_list()
        self.__update_params_table()
        self.__update_steps_list()

    def __save_test_data(self):
        if self.group_field.text() == "":
            show_custom_dialog("The GROUP field is required.", QMessageBox.Icon.Critical)
        elif self.step_list_widget.count() == 0:
            show_custom_dialog("At least 1 STEP is required.", QMessageBox.Icon.Critical)
        else:
            self.test_file_controller.test_data.group = self.group_field.text()
            self.test_file_controller.test_data.model = self.model_field.text()
            self.test_file_controller.test_data.customer = self.customer_field.text()
            self.test_file_controller.test_data.input_type = self.input_type_field.currentText()
            self.test_file_controller.input_sources = [self.v1_input_field.text(), self.v2_input_field.text(),
                                                       self.v3_input_field.text()]
            if self.is_editing:
                confirmation = self.test_file_controller.save_data("", True)
                show_custom_dialog(confirmation, QMessageBox.Icon.Information)
                self.close()
            else:
                directory = QFileDialog.getExistingDirectory(self, "Select a Directory",
                                                             self.config.get(TEST_FILES_DIR))
                if directory:
                    confirmation = self.test_file_controller.save_data(directory)
                    show_custom_dialog(confirmation, QMessageBox.Icon.Information)
                    self.close()

    def __clear_fields(self):
        confirmation = QMessageBox.question(
            self,
            "Confirm Action",
            "Are you sure you want to clear all fields?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirmation == QMessageBox.StandardButton.Yes:
            self.group_field.setText("")
            self.model_field.setText("")
            self.customer_field.setText("")
            self.input_type_field.setCurrentIndex(0)
            self.v1_input_field.setText("")
            self.v2_input_field.setText("")
            self.v3_input_field.setText("")
            self.test_file_controller = TestFileController()
            self.__update_channels_list()
            self.__update_params_table()
            self.__update_steps_list()

    def __show_step_setup_dialog(self, edit: bool = False):
        input_sources = [self.v1_input_field.text(), self.v2_input_field.text(), self.v3_input_field.text()]
        input_type = self.input_type_field.currentText()
        if edit:
            step_id = get_selected_item_id(self.step_list_widget)
            if step_id:
                step = self.test_file_controller.get_step(step_id)
                dialog = StepSetupDialog(input_sources, input_type, self.test_file_controller.active_channels,
                                         self.test_file_controller.params, step, self)
                if dialog.exec():
                    step.update(dialog.get_values())
                    self.__update_steps_list()
        else:
            if self.channel_list_widget.count() == 0:
                show_custom_dialog("Cannot add STEP: Channels setup list is empty.", QMessageBox.Icon.Warning)
            elif self.params_table.rowCount() == 0:
                show_custom_dialog("Cannot add STEP: Parameters list is empty.", QMessageBox.Icon.Warning)
            else:
                dialog = StepSetupDialog(input_sources, input_type, self.test_file_controller.active_channels,
                                         self.test_file_controller.params, None, self)
                if dialog.exec():
                    self.test_file_controller.add_step(dialog.get_values())
                    self.__update_steps_list()

    def __show_param_setup_dialog(self, edit: bool = False):
        if edit:
            param_id = get_selected_item_id(self.params_table)
            if param_id:
                param = self.test_file_controller.get_param(param_id)
                dialog = ParamsSetupDialog(param, self)
                if dialog.exec():
                    param.update(dialog.get_values())
                    self.__update_params_table()
        else:
            dialog = ParamsSetupDialog(None, self)
            if dialog.exec():
                self.test_file_controller.add_param(dialog.get_values())
                self.__update_params_table()
                self.__update_params_table()

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
            self.test_file_controller.active_channels.update(dialog.get_values())
            self.__update_channels_list()

    def __move_step(self):
        step_id = get_selected_item_id(self.step_list_widget)
        if step_id:
            index = self.step_list_widget.currentIndex().row() + 1
            list_length = self.step_list_widget.count()
            dialog = StepPositionDialog(index, list_length)
            if dialog.exec():
                new_index = dialog.get_values()
                if new_index != index:
                    self.test_file_controller.move_step(step_id, new_index)
                    self.__update_steps_list()

    def __clone_step(self):
        step_id = get_selected_item_id(self.step_list_widget)
        if step_id:
            self.test_file_controller.clone_step(step_id)
            self.__update_steps_list()

    def __clone_param(self):
        param_id = get_selected_item_id(self.params_table)
        if param_id:
            self.test_file_controller.clone_param(param_id)
            self.__update_params_table()

    def __remove_param(self):
        param_id = get_selected_item_id(self.params_table)
        if param_id:
            if self.test_file_controller.check_param_in_steps(param_id):
                show_custom_dialog("Cannot be removed: The parameter is being used.",
                                   QMessageBox.Icon.Warning)
            else:
                self.test_file_controller.remove_param(param_id)
                self.__update_params_table()

    def __remove_channel(self):
        if self.step_list_widget.count() != 0:
            show_custom_dialog("Cannot be removed: Step list is not empty.", QMessageBox.Icon.Warning)
        else:
            channel_id = get_selected_item_id(self.channel_list_widget)
            if channel_id:
                self.test_file_controller.remove_channel(channel_id)
                self.__update_channels_list()

    def __remove_step(self):
        step_id = get_selected_item_id(self.step_list_widget)
        if step_id:
            self.test_file_controller.remove_step(step_id)
            self.__update_steps_list()

    def __update_channels_list(self):
        self.channel_list_widget.clear()
        for channel_id, label in self.test_file_controller.active_channels.items():
            item = QListWidgetItem(f"{channel_id} : {label}")
            item.setData(Qt.ItemDataRole.UserRole, channel_id)
            self.channel_list_widget.addItem(item)

    def __update_params_table(self):
        self.params_table.setRowCount(0)
        self.params_table.setRowCount(len(self.test_file_controller.params))
        for row, param in enumerate(self.test_file_controller.params):
            item = QTableWidgetItem(str(param["tag"]))
            item.setData(Qt.ItemDataRole.UserRole, param['id'])
            self.params_table.setItem(row, 0, item)
            self.params_table.setItem(row, 1, QTableWidgetItem(f"{param['va']}"))
            self.params_table.setItem(row, 2, QTableWidgetItem(f"{param['vb']}"))
            self.params_table.setItem(row, 3, QTableWidgetItem(f"{param['ia']}"))
            self.params_table.setItem(row, 4, QTableWidgetItem(f"{param['ib']}"))

    def __update_steps_list(self):
        self.step_list_widget.clear()
        for index, step in enumerate(self.test_file_controller.steps):
            item = QListWidgetItem(f"{index + 1} - {step['description']}")
            item.setData(Qt.ItemDataRole.UserRole, step['id'])
            self.step_list_widget.addItem(item)

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
        v_params_container_layout.addWidget(self.params_table)

        # Main
        h_main_layout.addWidget(test_details_groupbox)
        h_main_layout.addWidget(steps_groupbox)
        h_main_layout.addWidget(params_groupbox)

        return h_main_layout

    def closeEvent(self, event: QCloseEvent) -> None:
        self.parent_window.show()
        event.accept()
