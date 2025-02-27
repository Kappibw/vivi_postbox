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

# Restart services (you may want to disable any conflicting network managers)
sudo systemctl mask wpa_supplicant
sudo systemctl disable wpa_supplicant
sudo systemctl stop wpa_supplicant
sleep 2
echo "Stopped wpa_supplicant"

# Ensure hostapd is not masked
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl restart hostapd

# Set up static IP on wlan0
bash "${SCRIPT_DIR}/setup_static_ip.sh"
echo "Letting static ip take effect"
sleep 4
sudo systemctl restart dnsmasq
sleep 2
echo "Started hostapd"

#!/bin/bash
# Kill any process using port 80
PORT=80
PID=$(lsof -t -i :$PORT)
if [ -n "$PID" ]; then
    echo "Port $PORT is in use by PID $PID, killing it..."
    sudo kill -9 $PID
else
    echo "Port $PORT is free."
fi
# Start the captive portal web server (using nohup so it runs in the background)
nohup python3 -u /home/pi/git/vivi_postbox/captive_portal/captive_portal.py > /var/log/captive_portal_stdout.log 2>&1 &

echo "Captive portal installed and started."
echo "SSID 'Vivi-Postbox' should now be visible. Connect to it and configure WiFi."
