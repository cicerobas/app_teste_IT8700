from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QGroupBox, QSlider, QVBoxLayout, QHBoxLayout, QWidget


class CustomFloatSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None, decimals=2):
        super().__init__(orientation, parent)
        self._min = 0.0
        self._max = 1.0
        self._step = 0.1
        self._decimals = decimals

    def set_range(self, min_val: float, max_val: float, step: float):
        self._min = min_val
        self._max = max_val
        self._step = step

        steps_count = int(round((max_val - min_val) / step))
        self.setRange(0, steps_count)

    def set_value(self, float_val: float):
        slider_val = int(round((float_val - self._min) / self._step))
        self.setValue(slider_val)


class ChannelMonitorView(QGroupBox):
    def __init__(self, channel_id: int):
        super().__init__()
        self.channel_id = channel_id
        self.setTitle(f"Channel {self.channel_id}")
        self.setFixedSize(QSize(350, 210))
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
        self.voltage_upper_label = QLabel("")
        self.voltage_lower_label = QLabel("")
        self.voltage_slider = CustomFloatSlider()
        self.voltage_slider.setEnabled(False)

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

    def set_limits(self, lower: float, upper: float):
        self.voltage_lower_label.setText(f"{lower}")
        self.voltage_upper_label.setText(f"{upper}")
        self.voltage_slider.set_range(lower, upper, 0.001)

    def get_values(self) -> dict[str, float]:
        return {"voltage": self.__voltage, "current": self.__current, "power": self.__power}

    def __setup_layout(self) -> QVBoxLayout:
        g_layout = QGridLayout()
        g_layout.setSpacing(0)
        g_layout.addWidget(self.voltage_label, 0, 0, 2, 1)
        g_layout.addWidget(self.current_label, 0, 1, 1, 1)
        g_layout.addWidget(self.power_label, 1, 1, 1, 1)

        v_main_layout = QVBoxLayout()
        slider_widget = QWidget()
        slider_widget.setFixedHeight(30)
        h_slider_layout = QHBoxLayout(slider_widget)
        h_slider_layout.addWidget(self.voltage_lower_label)
        h_slider_layout.addWidget(self.voltage_slider)
        h_slider_layout.addWidget(self.voltage_upper_label)
        v_main_layout.addLayout(g_layout)
        v_main_layout.addWidget(slider_widget)
        return v_main_layout

    def __update_displays(self):
        self.voltage_slider.set_value(self.__voltage)
        self.voltage_label.setText(f"{'%.2f' % self.__voltage if self.__voltage >= 10 else '%.3f' % self.__voltage} V")
        self.current_label.setText(f"{'%.2f' % self.__current if self.__current >= 10 else '%.2f' % self.__current} A")
        self.power_label.setText(f"{'%.2f' % self.__power} W")
