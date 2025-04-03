from PySide6.QtCore import QObject, Signal, QThreadPool

from controllers.electronic_load_controller import ElectronicLoadController
from models.test_file_model import TestData
from utils.monitor_worker import MonitorWorker
from views.channel_monitor_view import ChannelMonitorView


class WorkerSignals(QObject):
    update_output = Signal()


class TestController:
    def __init__(self, test_data: TestData):
        # Data
        self.test_data = test_data
        self.channel_list: list[ChannelMonitorView] = []
        # Instances
        self.electronic_load_controller = ElectronicLoadController()
        self.worker_signals = WorkerSignals()
        self.thread_pool = QThreadPool()
        self.monitoring_worker = None

        # Signals
        self.worker_signals.update_output.connect(self.update_output_display)

        # Teste
        print(self.electronic_load_controller.inst_id)
        if self.electronic_load_controller.conn_status:
            self.start_monitoring()

    def update_output_display(self):
        for channel in self.channel_list:
            voltage_value = self.electronic_load_controller.get_channel_value(channel.channel_id)
            channel.set_values((float(voltage_value), None))

    def start_monitoring(self):
        if self.monitoring_worker is None:
            self.monitoring_worker = MonitorWorker(self.worker_signals)
            self.thread_pool.start(self.monitoring_worker)
        else:
            self.monitoring_worker.resume()
