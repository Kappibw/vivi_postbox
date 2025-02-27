#!/bin/bash
# captive_portal/revert_to_client.sh
# This script reverts the Raspberry Pi from AP (captive portal) mode back to normal client mode.
# It stops hostapd and dnsmasq, flushes wlan0's IP addresses, and toggles NetworkManager to re-establish
# the client Wi-Fi connection.
#
# Run this script with root privileges.

echo "Reverting from AP mode (captive portal) to normal client mode..."

# Stop the AP services
echo "Stopping hostapd and dnsmasq..."
sudo systemctl stop hostapd
sudo systemctl stop dnsmasq

# Flush any IP addresses from wlan0 so that NetworkManager can assign a new one
echo "Flushing IP addresses on wlan0..."
sudo ip addr flush dev wlan0

# Restart wpa_supplicant
echo "Restarting wpa_supplicant"
sudo systemctl unmask wpa_supplicant
sleep 2
sudo systemctl restart wpa_supplicant

# Toggle NetworkManager to force a re-read of your connection profiles
echo "Restarting NetworkManager..."
sudo nmcli networking off
sleep 2
sudo nmcli networking on

# Allow a few seconds for the connection to re-establish
echo "Waiting for the network to reinitialize..."
sleep 2

# Display current network settings for debugging
echo "Current IP addresses on wlan0:"
ip addr show wlan0
echo "Current routing table:"
ip route show

echo "Reversion to client mode complete. You should now be connected to your normal Wi-Fi network."
