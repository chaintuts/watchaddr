# This code watches cryptocurrency addresses on ESP8266 microcontrollers
#
# Author: Josh McIntyre
#

import auth
import network
import urequests
import machine
import ssd1306
import time

class WatchAddress:

    # Define the base API endpoint
    API_ENDPOINT = "https://jmcintyre.net/sites/watchaddr/watchaddr.py"

    # Supported output types
    OUTPUT_DISPLAY = 0
    OUTPUT_SERIAL = 1

    # Supported units
    UNITS_CURR = 0
    UNITS_USD = 1

    # Polling interval, in seconds
    POLLING_INTERVAL = 30

    # Initialize the WatchAddr instance
    def __init__(self, output=OUTPUT_DISPLAY, units=UNITS_CURR, polling_interval=POLLING_INTERVAL):

        self.output = output
        if self.output == self.OUTPUT_DISPLAY:
            self.init_oled()

        self.units = units
        self.polling_interval = polling_interval

    # Connect to the wifi access point configured in auth.py
    def connect_wifi(self):

        conn = network.WLAN(network.STA_IF)
        conn.active(True)

        conn.connect(auth.SSID, auth.PASS)

        return conn.active()

    # Fetch the address balance inVformation from the API endpoint
    def get_balance(self, currency, address):

        url_full = self.API_ENDPOINT + "/" + address + "/" + currency
        ret = urequests.get(url_full)
        
        raw = ret.text
        bal, usd = raw.split(",")

        if self.units == self.UNITS_USD:
            return "$" + usd
        else:
            return bal

    # Initialize the OLED screen for display
    def init_oled(self):

        i2c = machine.I2C(-1, machine.Pin(5), machine.Pin(4))
        self.oled = ssd1306.SSD1306_I2C(128, 32, i2c)
        self.oled_line = 0

    # Clear the output - this really only applies to screens,
    # but the output functions should be generic
    def output_clear(self):

        if self.output == self.OUTPUT_DISPLAY:
            self.oled.fill(0)
            self.oled.show()

    # Define a flexible display function
    # This can simply print to serial or output to a peripheral
    def output_data(self, data):
        if self.output == self.OUTPUT_DISPLAY:

            self.oled.text(data, 0, self.oled_line)
            self.oled.show()

            # If the three lines are filled up, reset
            if self.oled_line == 20:
                self.oled_line = 0
            else:
                self.oled_line = self.oled_line + 10
        else:
            print(data)

    # Poll for the desired data every N seconds
    def poll_balance(self):

        while True:
            self.output_clear()
            for addr in auth.ADDRS:
                try:
                    bal = self.get_balance(addr[0], addr[1])
                    self.output_data(addr[0] + ": " + str(bal))
                except OSError:
                    self.output_data("Err: bal fetch")
            time.sleep(self.polling_interval)


# This is the main entry point for the program
def main():

    wa = WatchAddress(units=WatchAddress.UNITS_USD)
    conn = wa.connect_wifi()
    if not conn:
        wa.output_data("Err: wifi conn")
    else:
        wa.poll_balance()
