from time import sleep

from PySide6.QtCore import QRunnable, QMutex, QWaitCondition, QMutexLocker


class MonitorWorker(QRunnable):
    def __init__(self, signals):
        super().__init__()
        self.mutex = QMutex()
        self.wait_condition = QWaitCondition()
        self.signals = signals
        self.paused = False
        self.running = True

    def run(self):
        while self.running:
            self.mutex.lock()
            while self.paused:
                self.wait_condition.wait(
                    self.mutex
                )
            self.mutex.unlock()

            self.signals.update_output.emit()
            sleep(0.1)

    def pause(self):
        with QMutexLocker(self.mutex):
            self.paused = True

    def resume(self):
        with QMutexLocker(self.mutex):
            self.paused = False
            self.wait_condition.wakeAll()

    def stop(self):
        with QMutexLocker(self.mutex):
            self.running = False
            self.paused = False
            self.wait_condition.wakeAll()
