from PySide6.QtCore import QSize, Qt
from PySide6.QtWidgets import QGridLayout, QLabel, QGroupBox, QSlider, QVBoxLayout, QHBoxLayout, QWidget


class CustomFloatSlider(QSlider):
    def __init__(self, orientation=Qt.Orientation.Horizontal, parent=None, decimals=2):
        super().__init__(orientation, parent)
        self._min = 0.0
        self._max = 1.0
        self._step = 0.1
        self._decimals = decimals

    def set_range(self, min_val: float, max_val: float, step: float) -> None:
        self._min = min_val
        self._max = max_val
        self._step = step

        steps_count = int(round((max_val - min_val) / step))
        self.setRange(0, steps_count)

    def set_value(self, float_val: float) -> None:
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
        self._voltage: float = 0
        self._current: float = 0
        self._power: float = 0

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

        self.setLayout(self._setup_layout())

    def set_values(self, values: tuple[float | None, float | None]) -> None:
        """Updates channel monitor values. If a value is None, the previous value is maintained."""
        voltage, current = values

        self._voltage = voltage if voltage is not None else self._voltage
        self._current = current if current is not None else self._current
        self._power = self._voltage * self._current
        self._update_displays()

    def set_limits(self, lower_limit: float, upper_limit: float) -> None:
        self.voltage_lower_label.setText(f"{lower_limit}")
        self.voltage_upper_label.setText(f"{upper_limit}")
        self.voltage_slider.set_range(lower_limit, upper_limit, 0.001)

    def get_display_values(self) -> dict[str, float]:
        return {"voltage": self._voltage, "current": self._current, "power": self._power}

    def _setup_layout(self) -> QVBoxLayout:
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

    def _update_displays(self) -> None:
        self.voltage_slider.set_value(self._voltage)
        self.voltage_label.setText(f"{'%.2f' % self._voltage if self._voltage >= 10 else '%.3f' % self._voltage} V")
        self.current_label.setText(f"{'%.2f' % self._current if self._current >= 10 else '%.2f' % self._current} A")
        self.power_label.setText(f"{'%.2f' % self._power} W")
