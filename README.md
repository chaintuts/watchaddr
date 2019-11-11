## General
____________

### Author
* Josh McIntyre

### Website
* jmcintyre.net

### Overview
* WatchAddr fetches address balance information using an ESP microcontroller

## Development
________________

### Git Workflow
* master for releases (merge development)
* development for bugfixes and new features

### Building
* make build
Build the application
* make clean
Clean the build directory

### Features
* Retrieve address balance information on a Wifi-enabled microprocessor
* Display via a serial connection

### Requirements
* Requires MicroPython

### Platforms
* Adafruit Feather Huzzah ESP8266 Wifi

## Usage
____________

### General usage
* Update auth_sample.py to auth.py using your Wifi configuration and addresses
* Push code to your microcontroller using the ampy tool: ampy --port <port> --baud 115200 put watchaddr.py (repeat with your auth.py)
* Connect to your board using your preferred serial connection (like PuTTY) to enter the MicroPython REPL
* Run import watchaddr
* Run watchaddr.main()

### Security note
* The ESP8266 has a very small buffer for TLS connections, and the BlockCypher API overflows every time. 
Therefore, this utility currently uses plain HTTP connections for fetching balance data.
This can expose the addresses you're looking at to another party.
