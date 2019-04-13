import logging
import voluptuous
from ZteClient import ZteClient

import homeassistant.helpers.config_validation as cv
from homeassistant.components.device_tracker import (
    DOMAIN, PLATFORM_SCHEMA, DeviceScanner)
from homeassistant.const import (
    CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_DEVICES, CONF_EXCLUDE)

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    voluptuous.Optional(CONF_HOST, default='10.0.0.20'): cv.string,
    voluptuous.Optional(CONF_USERNAME, default='admin'): cv.string,
    voluptuous.Required(CONF_PASSWORD): cv.string,
    voluptuous.Optional(CONF_DEVICES, default=[]):
        voluptuous.All(cv.ensure_list, [cv.string]),
    voluptuous.Optional(CONF_EXCLUDE, default=[]):
        voluptuous.All(cv.ensure_list, [cv.string]),
})

def get_scanner(hass, config):
    info = config[DOMAIN]
    host = info.get(CONF_HOST)
    user = info.get(CONF_USERNAME)
    password = info.get(CONF_PASSWORD)
    tracked_devices = info.get(CONF_DEVICES)
    excluded_devices = info.get(CONF_EXCLUDE)

    scanner = ZteDeviceScanner(host, user, password,
                                   tracked_devices, excluded_devices)

    try:
        scanner.perform_login()
        return scanner
    except Exception:
        return None

class ZteDeviceScanner(DeviceScanner):

    def __init__(self, host, user, password, tracked_devices,
                 excluded_devices):
        import ZteClient
        self.tracked_devices = tracked_devices
        self.excluded_devices = excluded_devices
        self.results = []
        self.zte_client = ZteClient.ZteClient(password, host=host, user=user)
    
    def perform_login(self):
        self.zte_client.login()

    def perform_device_scan(self):
        self.perform_login()
        self.results = self.zte_client.get_connected_devices()

    def scan_devices(self):
        self.perform_device_scan
        
        devices = []

        for device in self.results:
            tracked = (not self.tracked_devices or
                       device.mac_address in self.tracked_devices or
                       device.host_name in self.tracked_devices)
            tracked = tracked and (not self.excluded_devices or not(
                device.mac_address in self.excluded_devices or
                device.host_name in self.excluded_devices))
            if tracked:
                devices.append(device.mac_address)
        return devices

    def get_device_name(self, device):
        parts = device.split("_")
        mac_address = parts[0]
        ap_mac_address = None
        if len(parts) > 1:
            ap_mac_address = parts[1]

        host_name = None
        for device in self.results:
            if device.mac_address == mac_address:
                host_name = device.name
                break

        if not host_name or host_name == "--":
            host_name = mac_address

        if ap_mac_address:
            ap_name = "Router"
            for device in self.results:
                if device.mac_address == ap_mac_address:
                    ap_name = device.host_name
                    break

            return host_name + " on " + ap_name

        return host_name
