#!/bin/bash
# captive_portal/install_captive_portal.sh
# This script installs the captive portal configuration and starts the AP and web server.
# Run this script with root privileges.

# Check if hostapd is installed; if not, install hostapd and dnsmasq.
if ! command -v hostapd >/dev/null 2>&1 || ! command -v dnsmasq >/dev/null 2>&1; then
    echo "One or more required packages are missing. Installing hostapd and dnsmasq..."
    sudo apt-get update
    sudo apt-get install -y hostapd dnsmasq
fi

echo "Installed hostapd and dnsmasq"

# Set the directory where captive portal config files are located (relative to this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Copy hostapd and dnsmasq config files to appropriate locations
cp "${SCRIPT_DIR}/hostapd.conf" /etc/hostapd/hostapd.conf
cp "${SCRIPT_DIR}/dnsmasq.conf" /etc/dnsmasq.conf

# set up the hostapd control interface
sudo mkdir -p /run/hostapd
sudo chown root:netdev /run/hostapd
sudo chmod 755 /run/hostapd

# Set up static IP on wlan0
bash "${SCRIPT_DIR}/setup_static_ip.sh"
sleep 2

# Restart services (you may want to disable any conflicting network managers)
sudo systemctl mask wpa_supplicant
sudo systemctl disable wpa_supplicant
sudo systemctl stop wpa_supplicant
# Ensure hostapd is not masked
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl restart hostapd
sudo systemctl restart dnsmasq

# Start the captive portal web server (using nohup so it runs in the background)
nohup python3 "${SCRIPT_DIR}/captive_portal.py" > /var/log/captive_portal.log 2>&1 &

echo "Captive portal installed and started."
echo "SSID 'Vivi-Postbox' should now be visible. Connect to it and configure WiFi."
