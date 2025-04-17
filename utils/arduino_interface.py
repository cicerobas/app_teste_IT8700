import serial

from utils.config_manager import ConfigManager
from utils.constants import ARDUINO_SERIAL_PORT, ARDUINO_BAUD_RATE, ARDUINO_READ_TIMEOUT


class Arduino:
    def __init__(self):
        self.config = ConfigManager()
        self.conn = serial.Serial(self.config.get(ARDUINO_SERIAL_PORT), self.config.get(ARDUINO_BAUD_RATE))
        self.conn.timeout = ARDUINO_READ_TIMEOUT

    def set_pin_mode(self, pin_number: int, mode: str) -> None:
        """
        Performs a pinMode() operation on pin_number.
        Internally sends b'M{mode}{pin_number} where mode could be:
         - I for INPUT
         - O for OUTPUT
         - P for INPUT_PULLUP
        """
        command = ("".join(("M", mode, str(pin_number)))).encode()
        self.conn.write(command)

    def digital_read(self, pin_number: int) -> int | None:
        """
        Performs a digital read on pin_number and returns the value (1 or 0).
        Internally sends b'RD{pin_number}' over the serial connection.
        """
        command = ("".join(("RD", str(pin_number)))).encode()
        self.conn.write(command)
        line_received = self.conn.readline().decode().strip()
        header, value = line_received.split(":")
        if header == ("D" + str(pin_number)):
            return int(value)

    def digital_write(self, pin_number: int, digital_value: int) -> None:
        """
        Writes the digital_value on pin_number.
        Internally sends b'WD{pin_number}:{digital_value}' over the serial connection.
        """
        command = ("".join(("WD", str(pin_number), ":", str(digital_value)))).encode()
        self.conn.write(command)
