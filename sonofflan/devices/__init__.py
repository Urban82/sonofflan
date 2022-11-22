from sonofflan.config import DeviceConfig
from sonofflan.devices.device import Device
from sonofflan.devices.plug import Plug
from sonofflan.devices.strip import Strip


def create_device(data: dict, config: DeviceConfig) -> Device:
    """Create the device based on its type

    Parameters
    ----------
    `data` : dict
        Dictionary with data coming from Zeroconf
    `config` : DeviceConfig
        Configuration for the device
    """

    if data['type'] == "plug":
        return Plug(data, config)
    if data['type'] == "strip":
        return Strip(data, config)
    return Device(data, config)
