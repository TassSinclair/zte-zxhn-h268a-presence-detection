import requests
import logging
import hashlib
from collections import namedtuple
import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename="debug.log",level=logging.DEBUG)

Device = namedtuple("Device", ["host_name", "ip_address", "ipv6_address", "mac_address"])
get_text = lambda element: element.text

class ZteClient():

    def __init__(self, password, host="10.0.0.20", user="admin"):
        self.host = host
        self.user = user
        self.password = password
        self.baseUrl = "http://{}/".format(host)
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.cookie_jar.set('_TESTCOOKIESUPPORT', '1')

    def login(self):
        try:
            login_token = self.__get_login_token()
            self.login_cookies = self.__post_login_and_get_cookies(login_token)

        except requests.exceptions.RequestException:
            _LOGGER.exception("failed to perform login")
            raise Exception("failed to perform login")

    def __get_login_token(self):
        loginTokenUrl = self.baseUrl + "function_module/login_module/login_page/logintoken_lua.lua"
        response = requests.get(loginTokenUrl, timeout=30, verify=False, cookies=self.cookie_jar)
        login_token = ET.fromstring(response.text).text
        _LOGGER.debug("got login token %s", login_token)
        return login_token

    def __post_login_and_get_cookies(self, login_token):
        encodedPassword = hashlib.sha256((self.password + login_token).encode('utf-8')).hexdigest()
        data = {'action': (None, 'login'), 'Username': (None, 'admin'), 'Password': (None, encodedPassword)}
        response = requests.post(self.baseUrl, timeout=30, verify=False, files=data, cookies=self.cookie_jar, allow_redirects=False)
        cookies = response.cookies
        self.cookie_jar.update(cookies)
        _LOGGER.debug("got login cookie: %s", cookies.items())
        requests.get(self.baseUrl, timeout=30, verify=False, cookies=cookies)
        return cookies

    def get_connected_devices(self):
        try:
            devices = self.__get_connected_devices("wlanDevice") + \
                self.__get_connected_devices("lanDevice")
            return devices
        except requests.exceptions.RequestException:
            _LOGGER.exception("failed to get devices devices")

    def __get_connected_devices(self, connection_type):
        device_list_url = self.baseUrl + "getpage.lua"
        params = {'pid': '1005', 'InstNum': '5', '_': '1', 'nextpage': 'home_{}_lua.lua'.format(connection_type)}
        response = requests.get(device_list_url, timeout=30, verify=False, cookies=self.cookie_jar, params=params)
        root = ET.fromstring(response.text)
        instances = root.find('OBJ_ACCESSDEV_ID').findall('Instance')
        devices = list(map(self.__instance_to_device, instances))
        _LOGGER.debug('found %s %s devices', len(devices), connection_type)
        return devices

    def __instance_to_device(self, instance):
        param_names = map(get_text, instance.findall('ParaName'))
        param_values = map(get_text, instance.findall('ParaValue'))
        params = dict(zip(param_names, param_values))
        return Device(params['HostName'], params['IPAddress'], params['IPV6Address'], params['MACAddress'])