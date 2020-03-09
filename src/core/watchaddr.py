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
    API_ENDPOINT = "https://jmcintyre.net/sites/watchaddr/watchaddr.py"
    
    # Define the name for an offline "cache mode" file
    CACHE_FILE = "cache.txt"

    # Supported output types
    OUTPUT_DISPLAY = 0
    OUTPUT_SERIAL = 1

    # Supported balance types
    BAL_INDIVIDUAL = 0
    BAL_TOTAL = 1

    # Supported units
    UNITS_CURR = 0
    UNITS_USD = 1

    # Polling interval, in seconds
    POLLING_INTERVAL = 30

    # Initialize the WatchAddr instance
    def __init__(self, output=OUTPUT_DISPLAY, units=UNITS_CURR, polling_interval=POLLING_INTERVAL, bal=BAL_INDIVIDUAL):

        self.output = output
        if self.output == self.OUTPUT_DISPLAY:
            self.init_oled()

        self.units = units
        self.bal = bal
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
            self.cache_clear()
            if self.bal == self.BAL_INDIVIDUAL:
                for addr in auth.ADDRS:
                    try:
                        bal = self.get_balance(addr[0], addr[1])
                        self.output_data(addr[0] + ": " + str(bal))
                        self.write_cache(addr[0] + ": " + str(bal))
                    except OSError:
                        self.output_data("Err: bal fetch")
            else:
                total = 0.0
                for addr in auth.ADDRS:
                    try:
                        bal = self.get_balance(addr[0], addr[1])
                        total = total + float(bal[1:])
                    except OSError:
                        self.output_data("Err: bal fetch")
                self.output_data("Total USD:")
                self.output_data("$" + str(total))
                self.write_cache("Total USD:")
                self.write_cache("$" + str(total))
            time.sleep(self.polling_interval)

    # Clear the cache file
    def cache_clear(self):

        open(self.CACHE_FILE, "w").close()
    
    # Write a line to the cache file
    def write_cache(self, line):

        with open(self.CACHE_FILE, "a") as f:
            f.write(line + "\n")
    
    # Read from a cache file for offline mode
    def read_cache(self):

        with open(self.CACHE_FILE) as f:
            for line in f:
                self.output_data(line.strip().rstrip())

# This is the main entry point for the program
def main():

    wa = WatchAddress(output=WatchAddress.OUTPUT_DISPLAY, units=WatchAddress.UNITS_CURR)
    conn = wa.connect_wifi()
    if not conn:
        wa.read_cache()
    else:
        # First, check the ability to actually fetch data on the network
        # If we can't connect, use the cache
        try:
            urequests.get(wa.API_ENDPOINT)
            wa.poll_balance()
        except OSError:
            wa.read_cache()
