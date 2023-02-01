from sonofflan.config import DeviceConfig
from sonofflan.devices.plug import Plug


def _parse_data(value: str | int | float) -> float:
    """Parse data from update"""

    if isinstance(value, str):
        return float(value)
    if isinstance(value, float):
        return value
    if isinstance(value, int):
        return value / 100.0

    return 0


class PowerPlug(Plug):
    """Sonoff plug with power meter

    Attributes
    ----------
    `voltage` : float
        The measured voltage
    `current` : float
        The measured current
    `power` : float
        The measured power
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

        self._voltage = None
        self._current = None
        self._power = None
        super().__init__(data, config)

    def _update(self, data: dict) -> None:
        """Internal update method

        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        """

        super()._update(data)
        self._voltage = _parse_data(data['data']['voltage'])
        self._current = _parse_data(data['data']['current'])
        self._power = _parse_data(data['data']['power'])

    def _repr(self) -> str:
        """Internal representation method"""

        return super()._repr() + f" V:{self._voltage}V C:{self._current}A P:{self._power}W"

    @property
    def voltage(self) -> float | None:
        """The measured voltage"""
        return self._voltage

    @property
    def current(self) -> float | None:
        """The measured current"""
        return self._current

    @property
    def power(self) -> float | None:
        """The measured power"""
        return self._power
