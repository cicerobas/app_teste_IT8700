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
        self.inst_resource = self._setup_connection()
        self.active_channel = 0

    def _setup_connection(self):
        """Configures the connection with the SAT instrument."""
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

    def _sat_write(self, command: str) -> None:
        """Sends a write [command] to the instrument."""
        self.inst_resource.write(command)

    def _sat_query(self, command: str) -> str:
        """
        Sends a query [command] to the instrument.
        Returns the response string.
        """
        return self.inst_resource.query(command)

    def _select_channel(self, channel_id: int) -> None:
        """Set the [channel_id] as active on the instrument."""
        if self.active_channel == channel_id:
            return

        self.active_channel = channel_id
        self._sat_write(f"{SELECT_CHANNEL}{channel_id}")

    def toggle_active_channels_input(self, channels: list[int], state: bool) -> None:
        """Toggles the [channels] input to [status]."""
        if not self.conn_status:
            return

        for channel in channels:
            self._select_channel(channel)
            self._sat_write(INPUT_ON if state else INPUT_OFF)

    def get_channel_value(self, channel_id: int) -> str | None:
        """Query the instrument channel for the current voltage reading."""
        if not self.conn_status:
            return None

        self._select_channel(channel_id)
        return self._sat_query(FETCH_VOLT)

    def set_channel_current(self, channel_id: int, load: float) -> None:
        """Sets the current on the instrument active channel."""
        if not self.conn_status:
            return

        self._select_channel(channel_id)
        self._sat_write(f"{SET_CURR}{load}")
        sleep(0.1)

    def toggle_short_mode(self, channel_id: int, state: bool) -> None:
        """Toggles the instrument [SHORT] mode."""
        if not self.conn_status:
            return

        self._select_channel(channel_id)
        self._sat_write(SHORT_ON if state else SHORT_OFF)

    def reset_instrument(self) -> None:
        """Sends the [RESET] command to the instrument."""
        if not self.conn_status:
            return

        self._sat_write(RESET)
