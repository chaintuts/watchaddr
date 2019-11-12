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
* Display on a 128x32 I2C OLED (up to 3 addresses at a time)

### Requirements
* Requires MicroPython

### Platforms
* Adafruit Feather Huzzah ESP8266 Wifi

## Usage
____________

### General usage
* Update auth_sample.py to auth.py using your Wifi configuration and addresses
* Configure your preferred display (OLED or serial back to your PC) in watchaddr.py
* Configure your preferred units in watchaddr.py (Base currency or USD)
* Push code to your microcontroller using the ampy tool: `ampy --port <port> --baud 115200 put watchaddr.py` (repeat with your `auth.py`)

### OLED display usage
* When pushing code using ampy (as stated above) also put `main.py` - this script will import and run watchaddr on boot

### Serial usage
* Connect to your board using your preferred serial connection (like PuTTY) to enter the MicroPython REPL
* Run import watchaddr
* Run watchaddr.main()

### Security
* WatchAddr now uses TLS to connect to the self-hosted, minimalist API endpoint to get data that fits in the
ESP8266's small TLS buffer
