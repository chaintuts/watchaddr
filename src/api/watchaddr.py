#!/usr/bin/python3

# This file contains code for a very lightweight address balance information API
# WatchAddr running on an ESP8266 device needs a very small response to process,
# otherwise the TLS buffer will overflow.
# Providing this simple "proxy" will allow more secure TLS instead of plain HTTP,
# and will avoid overflowing the 5KB buffer limit on small devices
#
# Author: Josh McIntyre
#

import web
import requests
import json
import threading

# Define important constants
web.config.debug = False

# Define URL handling
urls = (
		"/(.*)/(.*)", "address_info"
	)


# Define API endpoints
API_ENDPOINTS = {
                   # Currency : ( API base url, raw balance key, decimal places, price API url )
                   "BCH" : ( "http://rest.bitcoin.com/v2/address/details/", "balanceSat", 8,
			     "https://api.cryptonator.com/api/ticker/bch-usd" ),
                   "BTC" : ( "http://api.blockcypher.com/v1/btc/main/addrs/", "balance", 8, 
			     "https://api.cryptonator.com/api/ticker/btc-usd" ),
                   "LTC" : ( "http://api.blockcypher.com/v1/ltc/main/addrs/", "balance", 8,
			     "https://api.cryptonator.com/api/ticker/ltc-usd" ),
                   "ETH" : ( "http://api.blockcypher.com/v1/eth/main/addrs/", "balance", 18,
			     "https://api.cryptonator.com/api/ticker/eth-usd" )
                }

# This function is the main entry point for the program
# Process requests for calls to <address>/<currency>
class address_info:

	def GET(self, address, currency):

		web.header("Content-Type", "text/json")

		if not address:
			response = "Please specify an address"
			return response

		if not currency:
			response = "Please specify an address"
			return response
		
		# Fetch the data in multiple threads to reduce IO latency
		data = {}
		t_bal = threading.Thread(target=self.fetch_bal, args=(address, currency.upper(), data))
		t_price = threading.Thread(target=self.fetch_price, args=(address, currency.upper(), data))

		t_bal.start()
		t_price.start()
		t_bal.join()
		t_price.join()

		bal = data["bal"]
		price = data["price"]
		usd = bal * price

		# Return the data in the form of a comma-separated list
		response = "{0:.8f},{1:.2f}".format(bal,usd)
		return response

	def fetch_bal(self, address, currency, data):
		
		# First, fetch the balance in the base currency	
		url_base = API_ENDPOINTS[currency][0]
		url_full = url_base + address
		ret = requests.get(url_full)
        
		raw = json.loads(ret.text)
		bal_small = raw[API_ENDPOINTS[currency][1]]
		bal = bal_small / (10 ** API_ENDPOINTS[currency][2])

		# Return the data from the function in the data dictionary
		data["bal"] = bal

	def fetch_price(self, address, currency, data):

		# Next, fetch the current USD price
		ret = requests.get(API_ENDPOINTS[currency][3])
		raw = json.loads(ret.text)
		price = float(raw["ticker"]["price"])

		# Return the data from the function in the data dictionary
		data["price"] = price

if __name__ == "__main__":

	app = web.application(urls, globals())
	app.run()
