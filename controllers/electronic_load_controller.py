from time import sleep

import pyvisa

from utils.config_manager import ConfigManager
from utils.constants import SAT_RESOURCE_PATH, SAT_BAUD_RATE
from utils.scpi_commands import *


class ElectronicLoadController:
    def __init__(self):
        self.config = ConfigManager()
        self.rm = pyvisa.ResourceManager("@py")
        self.conn_status = False
        self.inst_id = ""
        self.inst_resource = self.__setup_connection()
        self.active_channel = 0

    def __setup_connection(self):
        """
        Configures the connection with the SAT instrument.
        :return: None.
        """
        if self.config.get(SAT_RESOURCE_PATH) in self.rm.list_resources():
            inst = self.rm.open_resource(self.config.get(SAT_RESOURCE_PATH))
            inst.baud_rate = self.config.get(SAT_BAUD_RATE)
            self.conn_status = True
            id_response = inst.query(INST_ID)
            self.inst_id = id_response.strip()
            inst.write(SYSTEM_REMOTE)
            inst.write(CLEAR_STATUS)

            return inst

        return None

    def __sat_write(self, command: str) -> None:
        """
        Sends a write command to the instrument.
        :param command: A write formated string.
        :return: None.
        """
        self.inst_resource.write(command)

    def __sat_query(self, command: str) -> str:
        """
        Sends a query command to the instrument.
        :param command: A query formated string.
        :return: The string response to the query.
        """
        return self.inst_resource.query(command)

    def __select_channel(self, channel_id: int) -> None:
        """
        Set the channel as active on the instrument.
        :param channel_id: Channel to be set.
        :return: None.
        """
        if self.active_channel == channel_id:
            return

        self.active_channel = channel_id
        self.__sat_write(f"{SELECT_CHANNEL}{channel_id}")

    def toggle_active_channels_input(self, channels: list[int], state: bool) -> None:
        """
        Toggle the channels input status.
        :param channels: A list of channel to be toggled.
        :param state: Bool to the desired state: ON/OFF.
        :return: None.
        """
        if not self.conn_status:
            return

        for channel in channels:
            self.__select_channel(channel)
            self.__sat_write(INPUT_ON if state else INPUT_OFF)

    def get_channel_value(self, channel_id: int) -> str | None:
        """
        Query the instrument channel for the current voltage reading.
        :param channel_id: Channel to be read.
        :return: Instrument response for the channel.
        """
        if not self.conn_status:
            return None

        self.__select_channel(channel_id)
        return self.__sat_query(FETCH_VOLT)

    def set_channel_current(self, channel_id: int, load: float) -> None:
        """
        Sets the active current on the instrument channel.
        :param channel_id: Channel to be set.
        :param load: Current (Amps) to be set.
        :return: None.
        """
        if not self.conn_status:
            return

        self.__select_channel(channel_id)
        self.__sat_write(f"{SET_CURR}{load}")
        sleep(0.1)

    def toggle_short_mode(self, channel_id: int, state: bool) -> None:
        """
        Activates or deactivates the instrument SHORT mode.
        :param channel_id: Channel to toggle SHORT mode.
        :param state: Bool to represent the SHORT mode on/off.
        :return: None.
        """
        if not self.conn_status:
            return

        self.__select_channel(channel_id)
        self.__sat_write(SHORT_ON if state else SHORT_OFF)

    def reset_instrument(self) -> None:
        """
        Sends the 'RESET' command to the instrument.
        :return: None.
        """
        if not self.conn_status:
            return

        self.__sat_write(RESET)
