from PySide6.QtCore import QObject, Signal, QTimer


class DelayManager(QObject):
    delay_completed = Signal()
    remaining_time_changed = Signal(int)

    def __init__(self):
        super().__init__()
        self.remaining_time = 0
        self.paused = False

    def start_delay(self, delay):
        self.remaining_time = delay
        self.__run_timer()

    def pause_resume(self):
        if self.paused:
            self.paused = False
            self.__run_timer()
        else:
            self.paused = True

    def __run_timer(self):
        if self.paused:
            return
        if self.remaining_time > 0:
            self.remaining_time -= 100
            self.remaining_time_changed.emit(self.remaining_time)
            QTimer.singleShot(100, self.__run_timer)
        else:
            self.delay_completed.emit()
