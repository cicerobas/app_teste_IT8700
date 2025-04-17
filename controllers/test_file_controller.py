import os
import time
from dataclasses import asdict

import yaml

from models.test_file_model import TestData
from utils.constants import AVAILABLE_CHANNELS


def gen_id() -> int:
    """Generates a time based ID."""
    return int(time.time() * 1000)


class TestFileController:
    def __init__(self):
        self.test_data: TestData = TestData()
        self.editing_file_path = ""
        self.input_sources = []
        self.active_channels = {}
        self.params = []
        self.steps = []

    def load_file_data(self, file_path: str) -> None:
        """Loads the [self.test_data] with the editing test file data."""
        with open(file_path, "r", encoding="utf-8") as file:
            data = yaml.safe_load(file)
        self.test_data = TestData(**data)
        self.editing_file_path = file_path
        for step in self.test_data.steps:
            self.steps.append(asdict(step))
        for param in self.test_data.params:
            self.params.append(asdict(param))
        self.active_channels = self.test_data.channels
        self.input_sources = self.test_data.input_sources

    def save_data(self, directory_path: str, is_editing: bool = False) -> str:
        """Creates the new test file or overwrites if [is_editing]."""
        self.test_data.input_sources = [int(value) if value != '' else 0 for value in self.input_sources]
        self.test_data.channels = self.active_channels
        self.test_data.params = self.params
        self.test_data.steps = self.steps

        test_data_dict = asdict(self.test_data)
        file_path = f"{os.path.dirname(self.editing_file_path) if is_editing else directory_path}/{self.test_data.group}.yaml"
        with open(file_path, 'w', encoding='utf-8') as file:
            yaml.dump(test_data_dict, file, allow_unicode=True, default_flow_style=False, sort_keys=False)

        return f"File saved in: {file_path}"

    def get_step(self, step_id: int) -> dict:
        return next((step for step in self.steps if step["id"] == step_id))

    def add_step(self, step_data: dict) -> None:
        self.steps.append({"id": gen_id(), **step_data})

    def remove_step(self, step_id: int) -> None:
        self.steps.remove(self.get_step(step_id))

    def clone_step(self, step_id: int) -> None:
        step = self.get_step(step_id)
        new_step = step.copy()
        new_step.update({"id": gen_id()})
        self.steps.append(new_step)

    def move_step(self, step_id: int, new_index: int) -> None:
        index = self.steps.index(self.get_step(step_id))
        step = self.steps.pop(index)
        self.steps.insert(new_index - 1, step)

    def check_param_in_steps(self, param_id: int) -> bool:
        checked_steps = []
        for step in self.steps:
            checked_steps.append(param_id in step["channel_params"].values())

        return True in checked_steps

    def remove_channel(self, channel_id: int) -> None:
        self.active_channels.pop(channel_id)

    def get_available_channels(self) -> list:
        return [channel_id for channel_id in AVAILABLE_CHANNELS if channel_id not in self.active_channels.keys()]

    def get_param(self, param_id: int) -> dict:
        return next((param for param in self.params if param['id'] == param_id))

    def add_param(self, data: dict) -> None:
        self.params.append({"id": gen_id(), **data})

    def remove_param(self, param_id: int) -> None:
        self.params.remove(self.get_param(param_id))

    def clone_param(self, param_id: int) -> None:
        param = self.get_param(param_id)
        new_param = param.copy()
        new_param.update({"id": gen_id()})
        self.params.append(new_param)
