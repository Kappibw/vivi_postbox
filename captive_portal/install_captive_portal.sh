#!/bin/bash
# captive_portal/install_captive_portal.sh
# This script installs the captive portal configuration and starts the AP and web server.
# Run this script with root privileges.

# Set the directory where captive portal config files are located (relative to this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy hostapd and dnsmasq config files to appropriate locations
cp "${SCRIPT_DIR}/hostapd.conf" /etc/hostapd/hostapd.conf
cp "${SCRIPT_DIR}/dnsmasq.conf" /etc/dnsmasq.conf

# Set up static IP on wlan0
bash "${SCRIPT_DIR}/setup_static_ip.sh"

# Restart services (you may want to disable any conflicting network managers)
sudo systemctl stop wpa_supplicant
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq

# Start the captive portal web server (using nohup so it runs in the background)
nohup python3 "${SCRIPT_DIR}/captive_portal.py" > /var/log/captive_portal.log 2>&1 &

echo "Captive portal installed and started."
echo "SSID 'Vivi-Postbox' should now be visible. Connect to it and configure WiFi."
