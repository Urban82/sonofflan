from sonofflan.config import DeviceConfig
from sonofflan.devices.device import Device


class Strip(Device):
    """Sonoff device with multiple statuses (a plug stripe)

    Attributes
    ----------
    `outlets` : list[int]
        Available outlets
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

        self._statuses = {}
        super().__init__(data, config)

    def _update(self, data: dict) -> None:
        """Internal update method

        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        """

        super()._update(data)
        for switch in data['data']["switches"]:
            self._statuses[switch['outlet']] = (switch['switch'] == 'on')

    def _repr(self) -> str:
        """Internal representation method"""

        return super()._repr() + f" status:{self._statuses}"

    def _check_outlet(self, outlet: int) -> None:
        """Check if the outlet is available"""

        if outlet not in self._statuses:
            raise ValueError(f"{self} doesn't have outlet {outlet}")

    @property
    def outlets(self) -> list[int]:
        """Available outlets"""

        return [x for x in self._statuses]

    def status(self, outlet: int) -> bool:
        """The status of the given outlet (on or off)

        Parameters
        ----------
        `outlet` : int
            Outlet ID
        """

        self._check_outlet(outlet)
        return self._statuses[outlet]

    def on(self, outlet: int) -> None:
        """Turn on the given outlet

        Parameters
        ----------
        `outlet` : int
            Outlet ID
        """

        self._check_outlet(outlet)
        self._logger.debug(f"Turn ON {self} {outlet}")
        self._send("/zeroconf/switches", {"switches": [{"switch": "on", "outlet": outlet}]})

    def off(self, outlet: int) -> None:
        """Turn off the given outlet

        Parameters
        ----------
        `outlet` : int
            Outlet ID
        """

        self._check_outlet(outlet)
        self._logger.debug(f"Turn OFF {self} {outlet}")
        self._send("/zeroconf/switches", {"switches": [{"switch": "off", "outlet": outlet}]})

    def toggle(self, outlet: int) -> None:
        """Toggle the given outlet status

        Parameters
        ----------
        `outlet` : int
            Outlet ID
        """

        self._check_outlet(outlet)
        self._logger.debug(f"Toggle {self} {outlet}")
        if self._statuses[outlet]:
            self.off(outlet)
        else:
            self.on(outlet)

    def refresh(self, outlet: int) -> None:
        """Refresh the given outlet status (send the same status currently set)

        Parameters
        ----------
        `outlet` : int
            Outlet ID
        """

        self._check_outlet(outlet)
        self._logger.debug(f"Refresh {self} {outlet}")
        if self._statuses[outlet]:
            self.on(outlet)
        else:
            self.off(outlet)
