from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QLineEdit, QDialogButtonBox, QDoubleSpinBox, QGridLayout, \
    QLabel, QWidget, QHBoxLayout, QCheckBox, QSpinBox, QPushButton


class ChannelSetupDialog(QDialog):
    def __init__(self, available_channels: list[int], data: tuple[int, str] | None, parent=None):
        super().__init__(parent)
        self.available_channels: list[str] = [str(channel) for channel in available_channels]
        self.data = data
        self.setWindowTitle("Channels")

        # Components
        self.channels_combobox = QComboBox()
        self.channels_combobox.addItems(self.available_channels)
        self.channel_label = QLineEdit(self.data[1] if self.data else "")

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Layout
        layout = QFormLayout(self)
        if not self.data:
            layout.addRow("Channel:", self.channels_combobox)
        layout.addRow("Label:", self.channel_label)
        layout.addWidget(self.button_box)

    def get_values(self) -> dict[int, str]:
        if self.data:
            return {self.data[0]: self.channel_label.text()}

        return {int(self.channels_combobox.currentText()): self.channel_label.text()}


def custom_double_spinbox(suffix: str) -> QDoubleSpinBox:
    spinbox = QDoubleSpinBox()
    spinbox.setRange(0, 80)
    spinbox.setSuffix(suffix)

    return spinbox


class ParamsSetupDialog(QDialog):
    def __init__(self, param_dict: dict | None, parent=None):
        super().__init__(parent)
        self.param = param_dict
        self.setWindowTitle("Parameters")

        # Components
        self.tag_label = QLineEdit()
        self.va_field = custom_double_spinbox("V")
        self.vb_field = custom_double_spinbox("V")
        self.ia_field = custom_double_spinbox("A")
        self.ib_field = custom_double_spinbox("A")

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        layout = QGridLayout(self)
        layout.addWidget(QLabel("TAG:"), 0, 0, 1, 1)
        layout.addWidget(QLabel("VA:"), 1, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel("IA:"), 2, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel("< VB:"), 1, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(QLabel("<  IB:"), 2, 2, 1, 1, Qt.AlignmentFlag.AlignRight)
        layout.addWidget(self.tag_label, 0, 1, 1, 3)
        layout.addWidget(self.va_field, 1, 1, 1, 1)
        layout.addWidget(self.ia_field, 2, 1, 1, 1)
        layout.addWidget(self.vb_field, 1, 3, 1, 1)
        layout.addWidget(self.ib_field, 2, 3, 1, 1)
        layout.addWidget(self.button_box, 3, 0, 1, 4, Qt.AlignmentFlag.AlignRight)

        if self.param:
            self.__set_field_values()

    def __set_field_values(self):
        self.tag_label.setText(self.param['tag'])
        self.va_field.setValue(self.param['va'])
        self.vb_field.setValue(self.param['vb'])
        self.ia_field.setValue(self.param['ia'])
        self.ib_field.setValue(self.param['ib'])

    def get_values(self):
        return {'tag': self.tag_label.text(), 'va': self.va_field.value(), 'vb': self.vb_field.value(),
                'ia': self.ia_field.value(), 'ib': self.ib_field.value()}


class CustomChannelParamWidget(QWidget):
    def __init__(self, channel_id: int, channel_label: str, params: list[dict]):
        super().__init__()
        self.channel_id = channel_id
        self.channel_label = channel_label
        self.params = params

        # Components
        self.enabled_checkbox = QCheckBox()
        self.enabled_checkbox.setChecked(True)
        self.channel_label = QLabel(f"{self.channel_id}: {self.channel_label}")
        self.params_combobox = QComboBox()
        self.params_combobox.addItems([param['tag'] for param in self.params])

        layout = QHBoxLayout(self)
        layout.addWidget(self.enabled_checkbox)
        layout.addWidget(self.channel_label)
        layout.addStretch(1)
        layout.addWidget(self.params_combobox, alignment=Qt.AlignmentFlag.AlignRight)

    def set_values(self, checked: bool, param_id: int | None):
        if checked:
            self.enabled_checkbox.setChecked(True)
            index = self.params.index(next((param for param in self.params if param['id'] == param_id)))
            self.params_combobox.setCurrentIndex(index)
        else:
            self.enabled_checkbox.setChecked(False)

    def get_values(self) -> tuple[bool, int, int]:
        param_id = self.params[self.params_combobox.currentIndex()].get("id")
        return self.enabled_checkbox.isChecked(), self.channel_id, param_id


class StepSetupDialog(QDialog):
    def __init__(self, input_sources: list[str], input_type: str, channels: dict[int, str], params: list[dict],
                 step: dict | None,
                 parent=None):
        super().__init__(parent)
        self.channels = channels
        self.params = params
        self.step = step

        self.setWindowTitle("Steps")

        # Components
        self.channel_params = [CustomChannelParamWidget(channel_id, label, self.params) for channel_id, label in
                               self.channels.items()]
        self.step_type_combobox = QComboBox()
        self.step_type_combobox.addItems(["1 - Direct Current", "2 - Current Limiting", "3 - Automatic Short"])
        self.step_type_combobox.currentIndexChanged.connect(self.__check_disable_duration_field)
        self.description_field = QLineEdit()
        self.duration_field = custom_double_spinbox("s")
        self.input_source_combox = QComboBox()
        self.input_source_combox.addItems(
            [f"{i + 1}: {value}V{input_type.lower()}" for i, value in enumerate(input_sources)])

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Layout
        layout = QFormLayout(self)
        layout.addRow("Step Type:", self.step_type_combobox)
        layout.addRow("Description:", self.description_field)
        layout.addRow("Duration:", self.duration_field)
        layout.addRow("Input Source:", self.input_source_combox)
        layout.addRow(QLabel("Channel - Parameters"))
        for channel_widget in self.channel_params:
            layout.addRow(channel_widget)

        layout.addWidget(self.button_box)

        if self.step:
            self.__set_step_values()

    def __check_disable_duration_field(self):
        if self.step_type_combobox.currentIndex() != 0:
            self.duration_field.setValue(0)
            self.duration_field.setEnabled(False)
        else:
            self.duration_field.setEnabled(True)

    def __set_step_values(self):
        self.step_type_combobox.setCurrentIndex(self.step.get("step_type") - 1)
        self.description_field.setText(self.step.get("description"))
        self.duration_field.setValue(self.step.get("duration"))
        self.input_source_combox.setCurrentIndex(self.step.get("input_source"))
        channel_params_dict = self.step.get("channel_params")
        for channel_widget in self.channel_params:
            if channel_widget.channel_id in channel_params_dict.keys():
                channel_widget.set_values(True, channel_params_dict.get(channel_widget.channel_id))
            else:
                channel_widget.set_values(False, None)

    def get_values(self):
        step_values = {
            "step_type": self.step_type_combobox.currentIndex() + 1,
            "description": self.description_field.text(),
            "duration": self.duration_field.value(),
            "input_source": self.input_source_combox.currentIndex(),
            "channel_params": {}
        }
        for channel_widget in self.channel_params:
            values = channel_widget.get_values()
            if values[0]:
                step_values["channel_params"].update({values[1]: values[2]})

        return step_values


class StepPositionDialog(QDialog):
    def __init__(self, index: int, list_length: int, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Move the step")

        # Components
        self.position_spinbox = QSpinBox()
        self.position_spinbox.setRange(1, list_length)
        self.position_spinbox.setValue(index)

        # Buttons
        self.button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        self.button_box.accepted.connect(self.accept)
        self.button_box.rejected.connect(self.reject)

        # Layout
        layout = QFormLayout(self)
        layout.addRow("New Position:", self.position_spinbox)
        layout.addWidget(self.button_box)

    def get_values(self):
        return self.position_spinbox.value()


class PasswordDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Authentication required")

        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.ok_button = QPushButton("OK")
        self.ok_button.clicked.connect(self.accept)

        layout = QFormLayout(self)
        layout.addRow("Password:", self.password_input)
        layout.addWidget(self.ok_button)

    def get_password(self) -> str:
        return self.password_input.text()
