from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QLineEdit, QDialogButtonBox, QDoubleSpinBox, QGridLayout, \
    QLabel


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

    def get_values(self) -> tuple[int, str]:
        if self.data:
            return self.data[0], self.channel_label.text()

        return int(self.channels_combobox.currentText()), self.channel_label.text()


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
