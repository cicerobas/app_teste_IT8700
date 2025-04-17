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

    def run(self) -> None:
        """Emits the [update_output] signal every 100ms, as long as the worker is running."""
        while self.running:
            self.mutex.lock()
            while self.paused:
                self.wait_condition.wait(
                    self.mutex
                )
            self.mutex.unlock()

            self.signals.update_output.emit()
            sleep(0.1)

    def pause(self) -> None:
        """Pauses the execution of the worker. The thread sleeps until [resume()] is called."""
        with QMutexLocker(self.mutex):
            self.paused = True

    def resume(self) -> None:
        """Resumes thread execution if it was paused."""
        with QMutexLocker(self.mutex):
            self.paused = False
            self.wait_condition.wakeAll()

    def stop(self) -> None:
        """Safely terminates the worker execution."""
        with QMutexLocker(self.mutex):
            self.running = False
            self.paused = False
            self.wait_condition.wakeAll()
