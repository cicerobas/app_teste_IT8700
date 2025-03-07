from PySide6.QtCore import QSettings

from utils.constants import *


class ConfigManager:
    def __init__(self):
        self.settings = QSettings("CEBRA", "IT8700")
        self.defaults = {
            TEST_FILES_DIR: "",
            SAT_RESOURCE_PATH: "ASRL/dev/ttyUSB0::INSTR",
            SAT_BAUD_RATE: 115200,
            ARDUINO_RESOURCE_PATH: "ASRL/dev/ttyACM0::INSTR",
            ARDUINO_SERIAL_PORT: "/dev/ttyACM0",
            ARDUINO_BAUD_RATE: 9600,
        }

    def get(self, key):
        """
        Obtém o valor de uma configuração.
        Se não existir, retorna o valor padrão definido no dicionário 'self.defaults'.
        """
        return self.settings.value(key, self.defaults.get(key))

    def set(self, key, value):
        """Define um valor para uma configuração."""
        self.settings.setValue(key, value)

    def list_configs(self):
        """Lista todas as configurações armazenadas."""
        self.settings.sync()
        return {key: self.get(key) for key in self.defaults.keys()}
