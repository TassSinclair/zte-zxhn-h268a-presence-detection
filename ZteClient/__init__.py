import requests
import logging
import xml.etree.ElementTree as ET

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename="debug.log",level=logging.DEBUG)

class ZteClient():
    
    def __init__(self, host=None, port=None, user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.baseUrl = "http://{}/".format(host)
        self.cookie_jar = requests.cookies.RequestsCookieJar()
        self.cookie_jar.set('_TESTCOOKIESUPPORT', '1')

    def login(self):
        try:
            login_token = self.__get_login_token()
            self.login_cookies = self.__post_login_and_get_cookies()


        except requests.exceptions.RequestException:
            _LOGGER.exception("failed to get a login token")

    def __get_login_token(self):
        loginTokenUrl = self.baseUrl + "function_module/login_module/login_page/logintoken_lua.lua"
        response = requests.get(loginTokenUrl, timeout=30, verify=False, cookies=self.cookie_jar)
        login_token = ET.fromstring(response.text).text
        _LOGGER.info("got login token {}".format(login_token))
        return login_token

    def __post_login_and_get_cookies(self):
        response = requests.post(self.baseUrl, timeout=30, verify=False, cookies=self.cookie_jar)
        _LOGGER.info("got login cookies {}".format(response.cookies.items()))
        return response.cookies
