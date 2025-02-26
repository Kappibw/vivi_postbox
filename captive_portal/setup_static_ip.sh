#!/bin/bash
# captive_portal/setup_ap.sh
# This script sets the static IP for wlan0 when running in AP mode.
sudo ip addr add 192.168.4.1/24 dev wlan0
sudo ip link set wlan0 up
