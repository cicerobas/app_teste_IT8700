from PySide6.QtWidgets import QDialog, QFormLayout, QComboBox, QLineEdit, QDialogButtonBox


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
