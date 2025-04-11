from models.test_file_model import TestData


class TestFileController:
    def __init__(self):
        self.test_data: TestData = TestData()
        self.input_sources = []
        self.active_channels = {}

    # Teste
    def show_data(self):
        self.test_data.input_sources = [int(value) if value != '' else 0 for value in self.input_sources]
        self.test_data.channels = self.active_channels
        print(self.test_data)
