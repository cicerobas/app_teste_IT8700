from PySide6.QtCore import QSize
from PySide6.QtWidgets import QGridLayout, QLabel, QGroupBox


class ChannelMonitorView(QGroupBox):
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id
        self.setTitle(f"Channel {self.channel_id}")
        self.setFixedSize(QSize(350, 180))
        self.setProperty("class", "channel_monitor")

        # Values
        self.__voltage: float = 0
        self.__current: float = 0
        self.__power: float = 0

        # Components
        self.voltage_label = QLabel("0 V")
        self.current_label = QLabel("0 A")
        self.power_label = QLabel("0 W")
        self.voltage_label.setObjectName("voltage_label")
        self.current_label.setObjectName("current_label")
        self.power_label.setObjectName("power_label")

        self.setLayout(self.__setup_layout())

    def set_values(self, values: tuple[float | None, float | None]) -> None:
        """
        Updates channel monitor values. If a value is None, the previous value is maintained.
        :param values: tuple (voltage, current)
        :return: None
        """
        voltage, current = values

        self.__voltage = voltage if voltage is not None else self.__voltage
        self.__current = current if current is not None else self.__current
        self.__power = self.__voltage * self.__current
        self.__update_displays()

    def get_values(self) -> dict[str, float]:
        return {"voltage": self.__voltage, "current": self.__current, "power": self.__power}

    def __setup_layout(self) -> QGridLayout:
        g_layout = QGridLayout()
        g_layout.setSpacing(0)
        g_layout.addWidget(self.voltage_label, 0, 0, 2, 1)
        g_layout.addWidget(self.current_label, 0, 1, 1, 1)
        g_layout.addWidget(self.power_label, 1, 1, 1, 1)

        return g_layout

    def __update_displays(self):
        self.voltage_label.setText(f"{'%.2f' % self.__voltage if self.__voltage >= 10 else '%.3f' % self.__voltage} V")
        self.current_label.setText(f"{'%.2f' % self.__current if self.__current >= 10 else '%.2f' % self.__current} A")
        self.power_label.setText(f"{'%.2f' % self.__power if self.__power < 100 else self.__power} W")
