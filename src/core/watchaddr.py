# This code watches cryptocurrency addresses on ESP8266 microcontrollers
#
# Author: Josh McIntyre
#

import auth
import network
import urequests
import json

class WatchAddress:

    # Define API endpoints
    API_ENDPOINTS = {
                        # Currency : ( API base url, raw balance key, decimal places )
                        "BCH" : ( "http://rest.bitcoin.com/v2/address/details/", "balanceSat", 8 ),
                        "BTC" : ( "http://api.blockcypher.com/v1/btc/main/addrs/", "balance", 8 ),
                        "LTC" : ( "http://api.blockcypher.com/v1/ltc/main/addrs/", "balance", 8 ),
                        "ETH" : ( "http://api.blockcypher.com/v1/eth/main/addrs/", "balance", 18 )
                    }

    # Supported output types
    OUTPUT_DISPLAY = 0
    OUTPUT_SERIAL = 1

    # Initialize the WatchAddr instance
    def __init__(self, output=OUTPUT_DISPLAY):

        self.output = output

    # Connect to the wifi access point configured in auth.py
    def connect_wifi(self):

        conn = network.WLAN(network.STA_IF)
        conn.active(True)

        conn.connect(auth.SSID, auth.PASS)

        return conn.active()

    # Fetch the address balance information from the API endpoint
    def fetch_raw(self, currency, address):

        url_base = self.API_ENDPOINTS[currency][0]
        url_full = url_base + address
        ret = urequests.get(url_full)
        
        raw = json.loads(ret.text)
        return raw

    # Get the balance in the smallest unit (Satoshi, etc.),
    # convert to base currency, and return
    def fetch_balance(self, currency, raw):

        bal_small = raw[self.API_ENDPOINTS[currency][1]]
        bal = bal_small / (10 ** self.API_ENDPOINTS[currency][2])

        return bal

    # Define a flexible display function
    # This can simply print to serial or output to a peripheral
    def output_data(self, data):
        if self.output == self.OUTPUT_DISPLAY:
            pass
        else:
            print(data)

    # Wrapper to fetch a desired currency balance
    def get_balance(self, currency, address):
        
        raw = self.fetch_raw(currency, address)
        bal = self.fetch_balance(currency, raw)

        return bal

# This is the main entry point for the program
def main():

    wa = WatchAddress(output=WatchAddress.OUTPUT_SERIAL)
    conn = wa.connect_wifi()
    if not conn:
        wa.output_data("Error connecting to wifi network")
    else:
        for addr in auth.ADDRS:
            try:
                bal = wa.get_balance(addr[0], addr[1])
                wa.output_data(addr[0] + ": " + str(bal))
            except OSError:
                wa.output_data("Error fetching " + addr[0] + " balance")
    
