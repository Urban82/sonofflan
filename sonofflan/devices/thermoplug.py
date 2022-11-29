from sonofflan.config import DeviceConfig
from sonofflan.devices.plug import Plug


class ThermoPlug(Plug):
    """Sonoff plug with thermometer

    Attributes
    ----------
    `sensor` : str
        The reported sensor type
    `temperature` : float
        The measured temperature
    `humidity` : int
        The measured humidity
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

        self._sensor = None
        self._temperature = None
        self._humidity = None
        super().__init__(data, config)

    def _update(self, data: dict) -> None:
        """Internal update method

        Parameters
        ----------
        `data` : dict
            Dictionary with data coming from Zeroconf
        """

        super()._update(data)
        self._sensor = data['data']['sensorType']
        self._temperature = float(data['data']['currentTemperature'])
        self._humidity = float(data['data']['currentHumidity'])

    def _repr(self) -> str:
        """Internal representation method"""

        return super()._repr() + f" sensor:{self._sensor} T:{self._temperature}° H:{self._humidity}%"

    @property
    def sensor(self) -> float | None:
        """The reported sensor type"""
        return self._sensor

    @property
    def temperature(self) -> float | None:
        """The measured temperature"""
        return self._temperature

    @property
    def humidity(self) -> float | None:
        """The measured humidity"""
        return self._humidity
