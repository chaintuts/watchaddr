# This file contains a make script for the WatchAddr application
#
# Author: Josh McIntyre
#

# This block defines makefile variables
SRC_FILES=src/core/*.py src/auth/*.py
API_FILES=src/api/*.py

BUILD_DIR=bin/watchaddr
API_DIR=bin/watchaddr/api

# This rule builds the application
build: $(SRC_FILES)
	mkdir -p $(BUILD_DIR)
	mkdir -p $(API_DIR)
	cp $(SRC_FILES) $(BUILD_DIR)
	cp $(API_FILES) $(API_DIR)

# This rule cleans the build directory
clean: $(BUILD_DIR)
	rm -r $(API_DIR)/*
	rm -r $(BUILD_DIR)/*
	rmdir $(BUILD_DIR)
