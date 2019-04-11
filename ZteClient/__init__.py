import requests
import logging

_LOGGER = logging.getLogger(__name__)
logging.basicConfig(filename="debug.log",level=logging.DEBUG)

class ZteClient():
    
    def __init__(self, host=None, port=None, user=None, password=None):
        self.host = host
        self.port = port
        self.user = user
        self.password = password
        self.baseUrl = "http://{}/".format(host)
        _LOGGER.info("Good to go")

    def login(self):
        loginTokenUrl = self.baseUrl + "function_module/login_module/login_page/logintoken_lua.lua"

        try:
            response = requests.get(loginTokenUrl, timeout=30, verify=False)
            _LOGGER.info(response.text)
        except requests.exceptions.RequestException:
            _LOGGER.exception("Error talking to API")

            # Maybe one day we will distinguish between
            # different errors..
            return False, None