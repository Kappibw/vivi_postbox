#!/bin/bash
# captive_portal/setup_static_ip.sh
# This script sets the static IP for wlan0 when running in AP mode.

# Flush any existing IP addresses on wlan0
sudo ip addr flush dev wlan0

# Add the static IP address
sudo ip addr add 192.168.4.1/24 dev wlan0

# Bring the interface up
sudo ip link set wlan0 up
