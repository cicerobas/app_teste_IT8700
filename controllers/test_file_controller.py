import time

from models.test_file_model import TestData
from utils.constants import AVAILABLE_CHANNELS


def gen_id() -> int:
    return int(time.time() * 1000)


class TestFileController:
    def __init__(self):
        self.test_data: TestData = TestData()
        self.input_sources = []
        self.active_channels = {}
        self.params = []

    # Teste
    def show_data(self):
        self.test_data.input_sources = [int(value) if value != '' else 0 for value in self.input_sources]
        self.test_data.channels = self.active_channels
        self.test_data.params = self.params
        print(self.test_data)

    def remove_channel(self, channel_id: int):
        self.active_channels.pop(channel_id)

    def get_available_channels(self):
        return [channel_id for channel_id in AVAILABLE_CHANNELS if channel_id not in self.active_channels.keys()]

    def get_param(self, param_id: int):
        return next((param for param in self.params if param['id'] == param_id))

    def add_param(self, data: dict):
        self.params.append({"id": gen_id(), **data})

    def remove_param(self, param_id: int):
        self.params.remove(next((param for param in self.params if param['id'] == param_id)))

    def clone_param(self, param_id: int):
        param = self.get_param(param_id)
        new_param = param.copy()
        new_param.update({"id": gen_id()})
        self.params.append(new_param)
