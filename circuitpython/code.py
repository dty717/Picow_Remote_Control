import wifi
import socketpool
from dir.main import MAIN_HTML_TEMPLATE
import time
import ssl
import microcontroller
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
from adafruit_hid.mouse import Mouse
# from _init import kbd,mouse
# from common.tool import FIX_Waiting, stringTokey

from adafruit_httpserver import Server, Request, Response, GET, POST

class TLSServerSocketPool:
    def __init__(self, pool, ssl_context):
        self._pool = pool
        self._ssl_context = ssl_context
    @property
    def AF_INET(self):
        return self._pool.AF_INET
    @property
    def SOCK_STREAM(self):
        return self._pool.SOCK_STREAM
    @property
    def SOL_SOCKET(self):
        return self._pool.SOL_SOCKET
    @property
    def SO_REUSEADDR(self):
        return self._pool.SO_REUSEADDR
    def socket(self, *args, **kwargs):
        socket = self._pool.socket(*args, **kwargs)
        return self._ssl_context.wrap_socket(socket, server_side=True)
    def getaddrinfo(self, *args, **kwargs):
        return self._pool.getaddrinfo(*args, **kwargs)


# Set up a keyboard device.
kbd = Keyboard(usb_hid.devices)

# Type lowercase 'a'. Presses the 'a' key and releases it.

mouse = Mouse(usb_hid.devices)

#CIRCUITPY_WIFI_SSID="@PHICOMM_00"
#CIRCUITPY_WIFI_PASSWORD="delin2016"
CIRCUITPY_WIFI_SSID="DESKTOP-18"
CIRCUITPY_WIFI_PASSWORD="12345678"
#CIRCUITPY_WIFI_SSID="iPhone"
#CIRCUITPY_WIFI_PASSWORD="12345678"

wifi.radio.connect(ssid = CIRCUITPY_WIFI_SSID, password = CIRCUITPY_WIFI_PASSWORD)
socket_pool = socketpool.SocketPool(wifi.radio)

ssl_context = ssl.create_default_context()
# The Pico is the server and does not require a certificate from the client, so disable
# certificate validation by explicitly specifying no verification CAs
ssl_context.load_verify_locations(cadata="")
ssl_context.load_cert_chain(
    "certificates/certificate-chain.pem", "certificates/key.pem"
)
tls_pool = TLSServerSocketPool(socket_pool, ssl_context)

pool = tls_pool
server = Server(pool, "/static", debug=True)

@server.route("/key/<key_event>/<key_code>", [GET, POST])
def perform_action(
    request: Request, key_event: str,key_code: str
):
    """
    Performs an "action" on a specified device.
    """
    key_code = int(key_code)
    if key_event == "up":
        kbd.release(key_code)
    elif key_event == "down":
        kbd.press(key_code)
    return Response(
        request, "{state:\"success\"}"
    )


server.serve_forever(str(wifi.radio.ipv4_address),port=443)
