import argparse
import asyncio
import json
import logging
import sys

from sonofflan.browser import Browser
from sonofflan.config import DevicesConfig
from sonofflan.devices import Device, Plug, Strip, PowerPlug, ThermoPlug

log_formatter = logging.Formatter("%(asctime)s %(levelname)s [%(name)s] %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(log_formatter)

root_logger = logging.getLogger()
root_logger.setLevel(logging.INFO)
root_logger.addHandler(stream_handler)

logger = logging.getLogger("sonofflan")


def discover(devices: dict[str, Device]) -> None:
    print(f"Found {len(devices)} devices:")
    for device_id in devices:
        device = devices[device_id]
        print(f" - {device.name} [{device.id}] {type(device).__name__}")


def info(devices: dict[str, Device], device_id: str) -> None:
    if device_id not in devices:
        logger.error(f"Device with ID {device_id} not found")
        return
    device = devices[device_id]
    print(f"{device.name} [{device.id}]")
    print(f"  Url:         {device.url}")
    print(f"  Type:        {type(device).__name__}")
    if isinstance(device, Plug):
        print(f"  Status:      {'on' if device.status else 'off'}")
    elif isinstance(device, Strip):
        s = ""
        for outlet in device.outlets:
            s += f" {outlet}:{'on' if device.status(outlet) else 'off'}"
        print(f"  Status:     {s}")
    if isinstance(device, PowerPlug):
        print(f"  Voltage:     {device.voltage}V")
        print(f"  Current:     {device.current}A")
        print(f"  Power:       {device.power}W")
    if isinstance(device, ThermoPlug):
        print(f"  Temperature: {device.temperature}°C")
        print(f"  Humidity:    {device.humidity}%")
        print(f"  Sensor:      {device.sensor}")


async def main() -> None:
    browser = None
    # noinspection PyBroadException
    try:
        logger.info("Creating Sonoff Zeroconfig browser...")
        browser = Browser(config)

        logger.info("Waiting for discovery")
        await asyncio.sleep(5)

        if args.action == "discover":
            discover(browser.devices)
        elif args.action == "info":
            info(browser.devices, args.device)
    except Exception:
        logger.error("Exception", exc_info=True)
    finally:
        logger.info("Shutting down...")
        if browser:
            await browser.shutdown()
        logger.info("Completed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="sonofflan",
        description="Simple utility to interact with Sonoff devices through LAN protocol"
    )
    parser.add_argument("action", choices=["discover", "info"], default="discover", nargs='?')
    logparser = parser.add_mutually_exclusive_group(required=False)
    logparser.add_argument("-v", "--verbose", help="Verbose", action="store_true", default=False)
    logparser.add_argument("-q", "--quiet", help="Quiet", action="store_true", default=False)
    parser.add_argument("-d", "--device", help="Device ID")
    parser.add_argument("-k", "--key", help="Device encryption key")
    parser.add_argument("-c", "--config", help="Device configuration", type=argparse.FileType("r"))
    args = parser.parse_args()
    if args.action == "info":
        if args.device is None:
            logger.error("Device ID is missing")
            sys.exit(1)

    if args.config is not None:
        config = DevicesConfig(json.load(args.config))
    elif args.device is not None:
        j = {"id": args.device}
        if args.key is not None:
            j["key"] = args.key
        config = DevicesConfig([j])
    else:
        config = DevicesConfig()

    if args.verbose:
        root_logger.setLevel(logging.DEBUG)
    if args.quiet:
        root_logger.setLevel(logging.WARNING)

    # noinspection PyBroadException
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
    except Exception:
        logger.error("Unhandled exception", exc_info=True)
