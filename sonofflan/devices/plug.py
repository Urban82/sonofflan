from sonofflan.config import DeviceConfig
from sonofflan.devices.device import Device


class Plug(Device):
    """Sonoff device with a status (a plug)

    Attributes
    ----------
    `status` : bool
        The status of the plug
    """

    def __init__(self, data: dict, config: DeviceConfig) -> None:
        """
        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        `config` : DeviceConfig
            Configuration for the device
        """

        self._status = None
        super().__init__(data, config)

    def _update(self, data: dict) -> None:
        """Internal update method

        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        """

        super()._update(data)
        self._status = (data['data']['switch'] == 'on')

    def _repr(self) -> str:
        """Internal representation method"""

        return super()._repr() + f" status:{self._status}"

    @property
    def status(self) -> bool | None:
        """The status of the plug (on or off)"""

        return self._status

    def on(self) -> None:
        """Turn on the plug"""

        self._logger.debug(f"Turn ON {self}")
        self._send("/zeroconf/switch", {"switch": "on"})

    def off(self) -> None:
        """Turn off the plug"""

        self._logger.debug(f"Turn OFF {self}")
        self._send("/zeroconf/switch", {"switch": "off"})

    def toggle(self) -> None:
        """Toggle the device status"""

        self._logger.debug(f"Toggle {self}")
        if self._status:
            self.off()
        else:
            self.on()

    def refresh(self) -> None:
        """Refresh the device status (send the same status currently set)"""

        self._logger.debug(f"Refresh {self}")
        if self._status:
            self.on()
        else:
            self.off()
