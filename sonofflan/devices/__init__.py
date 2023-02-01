from sonofflan.config import DeviceConfig
from sonofflan.devices.device import Device
from sonofflan.devices.plug import Plug
from sonofflan.devices.strip import Strip
from sonofflan.devices.powerplug import PowerPlug
from sonofflan.devices.thermoplug import ThermoPlug


def create_device(data: dict, config: DeviceConfig) -> Device:
    """Create the device based on its type

    Parameters
    ----------
    `data` : dict
        Dictionary with data coming from Zeroconf
    `config` : DeviceConfig
        Configuration for the device
    """

    # Checking if a "plug" is the new PowerPlug
    if data['type'] == "plug" and 'power' in data['data'] and 'voltage' in data['data'] and 'current' in data['data']:
        data['type'] = "enhanced_plug"

    if data['type'] == "plug":
        return Plug(data, config)
    if data['type'] == "strip":
        return Strip(data, config)
    if data['type'] == "enhanced_plug":
        return PowerPlug(data, config)
    if data['type'] == "th_plug":
        return ThermoPlug(data, config)
    return Device(data, config)
