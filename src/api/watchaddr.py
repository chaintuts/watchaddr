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

		# First, fetch the balance in the base currency	
		currency = currency.upper()
		url_base = API_ENDPOINTS[currency][0]
		url_full = url_base + address
		ret = requests.get(url_full)
        
		raw = json.loads(ret.text)
		bal_small = raw[API_ENDPOINTS[currency][1]]
		bal = bal_small / (10 ** API_ENDPOINTS[currency][2])

		# Next, calculate the current USD value
		ret = requests.get(API_ENDPOINTS[currency][3])
		raw = json.loads(ret.text)
		price = float(raw["ticker"]["price"])
		usd = bal * price

		# Return the data in the form of a comma-separated list
		response = "{0:.8f},{1:.2f}".format(bal,usd)
		return response

if __name__ == "__main__":

	app = web.application(urls, globals())
	app.run()
