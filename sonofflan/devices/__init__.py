from sonofflan.config import DeviceConfig
from sonofflan.devices.device import Device


def create_device(data: dict, config: DeviceConfig) -> Device:
    """Create the device based on its type

    Parameters
    ----------
    `data` : dict
        Dictionary with data coming from Zeroconf
    `config` : DeviceConfig
        Configuration for the device
    """

    return Device(data, config)
