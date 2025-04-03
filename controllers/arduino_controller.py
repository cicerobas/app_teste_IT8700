from contextlib import suppress
from time import sleep

import pyvisa

from utils.arduino_interface import Arduino
from utils.config_manager import ConfigManager
from utils.constants import ARDUINO_RESOURCE_PATH, ARDUINO_OUTPUT_PINS


class ArduinoController:
    """
    Used to control the connection with Arduino and run commands using pyduino interface.
    """

    def __init__(self):
        self.config = ConfigManager()
        self.rm = pyvisa.ResourceManager("@py")
        self.arduino = None

        arduino_path = self.config.get(ARDUINO_RESOURCE_PATH)
        if arduino_path in self.rm.list_resources():
            with suppress(Exception):
                self.arduino = Arduino()

        self.output_states = {pin: False for pin in ARDUINO_OUTPUT_PINS}
        self.active_input_source = 0

    def check_connection(self) -> bool:
        """
        Checks the connection status with the Arduino.
        :return: Connection status (bool).
        """
        return self.arduino is not None

    def set_active_pin(self, reset: bool) -> None:
        """
        Set active arduino output pins.
        :param reset: Flag to reset all pins to Off.
        :return: None.
        """
        if not self.check_connection():
            return

        for pin, state in self.output_states.items():
            if state:
                self.arduino.set_pin_mode(pin, "O")
                self.arduino.digital_write(pin, 0 if reset else 1)

    def set_input_source(self, input_source: int, input_type: str) -> None:
        """
        Defines the active input source:
         - Pino 4: CA1
         - Pino 5: CA2
         - Pino 6: CA3
         - Pino 7: CC1
         - Pino 8: CC2
         - Pino 9: CC3
         - Pino 10: Buzzer

        :param input_source: Represents the input source to set.
        :param input_type: Represents the input type variation.
        :return: None.
        """
        if self.active_input_source == input_source:
            return

        pin_mapping = {
            (1, "CA"): "4",
            (2, "CA"): "5",
            (3, "CA"): "6",
            (1, "CC"): "7",
            (2, "CC"): "8",
            (3, "CC"): "9",
        }

        if (input_source, input_type) in pin_mapping:
            self.change_output(pin_mapping[(input_source, input_type)])
            self.active_input_source = input_source

    def change_output(self, active_pin: str) -> None:
        """
        Resets all output pins, and activates the active_pin.
        :param active_pin: Represents the pin to be active.
        :return: None.
        """
        if not self.check_connection():
            return

        self.set_active_pin(True)
        self.output_states = {pin: (pin == active_pin) for pin in self.output_states}
        self.set_active_pin(False)

    def buzzer(self) -> bool:
        """
        Activates the buzzer alert.
        :return: Bool value indicating the alert done.
        """
        if not self.check_connection():
            return False

        self.arduino.set_pin_mode("10", "O")
        self.arduino.digital_write("10", 1)
        sleep(0.5)
        self.arduino.digital_write("10", 0)
        return True
