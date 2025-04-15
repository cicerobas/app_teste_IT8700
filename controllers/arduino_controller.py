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
        resources = self.rm.list_resources()
        if arduino_path in resources:
            self.arduino = Arduino()

        self.output_pins_state = {pin: False for pin in ARDUINO_OUTPUT_PINS}
        self.active_pin = 0

    def check_connection(self) -> bool:
        """
        Checks the connection status with the Arduino.
        :return: Connection status (bool).
        """
        return self.arduino is not None

    def setup_active_pin(self, reset: bool) -> None:
        """
        Set active arduino output pins.
        :param reset: Flag to reset all pins to Off.
        :return: None.
        """
        if not self.check_connection():
            return

        for pin, state in self.output_pins_state.items():
            if reset:
                self.arduino.digital_write(pin, 0)
            else:
                self.arduino.digital_write(pin, 1 if state else 0)
        sleep(1)

    def set_input_source(self, input_source: int, input_type: str) -> None:
        pin_mapping = {
            (0, "CA"): 4,
            (1, "CA"): 5,
            (2, "CA"): 6,
            (0, "CC"): 7,
            (1, "CC"): 8,
            (2, "CC"): 9,
        }

        if (input_source, input_type) in pin_mapping:
            self.change_output(pin_mapping[(input_source, input_type)])

    def change_output(self, active_pin: int) -> None:
        """
        Resets all output pins, and activates the active_pin.
        :param active_pin: Represents the pin to be active.
        :return: None.
        """
        if not self.check_connection() or self.active_pin == active_pin:
            return

        self.active_pin = active_pin
        self.setup_active_pin(True)
        self.output_pins_state.update({pin: pin == active_pin for pin in self.output_pins_state})
        self.setup_active_pin(False)

    def buzzer(self):
        """
        Activates the buzzer alert.
        :return: Bool value indicating the alert done.
        """
        if not self.check_connection():
            return False

        self.arduino.digital_write(10, 1)
        sleep(0.5)
        self.arduino.digital_write(10, 0)
