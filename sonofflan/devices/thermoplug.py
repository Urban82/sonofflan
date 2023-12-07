from sonofflan.config import DeviceConfig
from sonofflan.devices.plug import Plug


class ThermoPlug(Plug):
    """Sonoff plug with thermometer

    Attributes
    ----------
    `sensor` : str
        The reported sensor type
    `mode` : str
        The working mode ("normal" or automatic based on "temperature" or "humidity")
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
        self._mode = None
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
        self._mode = data['data']['deviceType']
        self._temperature = float(data['data']['currentTemperature'])
        self._humidity = int(data['data']['currentHumidity'])

    def _repr(self) -> str:
        """Internal representation method"""

        return super()._repr() + f" sensor:{self._sensor} T:{self._temperature}° H:{self._humidity}%"

    @property
    def sensor(self) -> str | None:
        """The reported sensor type"""
        return self._sensor

    @property
    def mode(self) -> str | None:
        """The working mode"""
        return self._mode

    @property
    def temperature(self) -> float | None:
        """The measured temperature"""
        return self._temperature

    @property
    def humidity(self) -> int | None:
        """The measured humidity"""
        return self._humidity

    def on(self) -> None:
        """Turn on the plug"""

        if self._mode != "normal":
            self._logger.warning(f"Cannot turn ON {self}: mode is {self._mode}")
            return

        super().on()

    def off(self) -> None:
        """Turn off the plug"""

        if self._mode != "normal":
            self._logger.warning(f"Cannot turn OFF {self}: mode is {self._mode}")
            return

        super().off()

    def toggle(self) -> None:
        """Toggle the device status"""

        if self._mode != "normal":
            self._logger.warning(f"Cannot toggle {self}: mode is {self._mode}")
            return

        super().toggle()

    def refresh(self) -> None:
        """Refresh the device status (send the same status currently set)"""

        if self._mode != "normal":
            self._logger.warning(f"Cannot refresh {self}: mode is {self._mode}")
            return

        super().refresh()
