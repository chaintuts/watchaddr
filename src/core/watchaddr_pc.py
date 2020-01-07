# This code watches cryptocurrency addresses on ESP8266 microcontrollers
#
# Author: Josh McIntyre
#

import auth
import requests
import time

class WatchAddress:

    # Define the base API endpoint
    API_ENDPOINT = "https://jmcintyre.net/sites/watchaddr/watchaddr.py"

    # Fetch the address balance inVformation from the API endpoint
    def get_balance(self, currency, address):

        url_full = self.API_ENDPOINT + "/" + address + "/" + currency
        ret = requests.get(url_full)
        
        raw = ret.text
        bal, usd = raw.split(",")

        return (bal, "$" + usd)

    # Get all information and print to standard out
    def get_all(self):
        total = 0.0
        for addr in auth.ADDRS:
            try:

                # Get and print the individual address balance
                data = self.get_balance(addr[0], addr[1])
                print(f"{addr[0]} : {data[0]}, {data[1]}")

                # Add to the total
                # Strip off the $ character before casting
                total = total + float(data[1][1:])
            except OSError:
                self.output_data("Err: bal fetch")

        # Display the total
        print(f"Total USD value: ${total:.2f}")

# This is the main entry point for the program
def main():

    wa = WatchAddress()
    wa.get_all()

if __name__ == "__main__":
    main()
