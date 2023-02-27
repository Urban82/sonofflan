from sonofflan.config import DeviceConfig
from sonofflan.devices.device import Device
from sonofflan.errors import MissingSwitchesError


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
        self._outlet = None
        super().__init__(data, config)

    def _update(self, data: dict) -> None:
        """Internal update method

        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        """

        super()._update(data)
        if "switch" in data['data']:
            self._status = (data['data']['switch'] == 'on')
        elif "switches" in data['data']:
            if len(data['data']['switches']) == 0:
                raise MissingSwitchesError(self.id, data["type"])
            if len(data['data']['switches']) > 1:
                self._logger.warning(
                    f'Too much switches in device "{self.id}" ({data["type"]}): using only the first one'
                )
            self._outlet = data['data']['switches'][0]['outlet']
            self._status = (data['data']['switches'][0]['switch'] == 'on')
        else:
            raise MissingSwitchesError(self.id, data["type"])

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
        if self._outlet is None:
            self._send("/zeroconf/switch", {"switch": "on"})
        else:
            self._send("/zeroconf/switches", {"switches": [{"switch": "on", "outlet": self._outlet}], "operSide": 1 })

    def off(self) -> None:
        """Turn off the plug"""

        self._logger.debug(f"Turn OFF {self}")
        if self._outlet is None:
            self._send("/zeroconf/switch", {"switch": "off"})
        else:
            self._send("/zeroconf/switches", {"switches": [{"switch": "off", "outlet": self._outlet}], "operSide": 1})

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
