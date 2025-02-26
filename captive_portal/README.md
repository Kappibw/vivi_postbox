# Captive Portal Setup

This directory contains the files and scripts needed to set up a captive portal for the Pi.

## Files

- **hostapd.conf**: Configuration for hostapd to broadcast the "Vivi-Postbox" access point.
- **dnsmasq.conf**: Configuration for dnsmasq to provide DHCP and DNS redirection.
- **setup_static_ip.sh**: Script to assign a static IP (192.168.4.1) to wlan0.
- **captive_portal.py**: A simple Flask web server that serves the captive portal page.
- **templates/portal.html**: HTML template for the captive portal page.
- **install_captive_portal.sh**: Script to copy configuration files to their system locations, set up the network, and start services.

## Installation

1. **Ensure your Pi is updated and that hostapd, dnsmasq, and Python (with Flask) are installed:**

   ```bash
   sudo apt update && sudo apt install hostapd dnsmasq python3-flask
   ```

2. **Run the installation script as root:**

    ```bash
    sudo bash install_captive_portal.sh
    ```
3. **Connect to the WiFi** network named `Vivi-Postbox` on your phone or laptop.

4. **Open a browser** (if not automatically redirected) and navigate to any web page; you should be redirected to the captive portal where you can enter your WiFi credentials.

5. **Once credentials are submitted**, the Pi will attempt to connect to the new network (this part is left for you to implement in the captive portal server).

## Customization

- **SSID and Channel:** Edit hostapd.conf to change the SSID or other settings.

- **IP Range:** Modify dnsmasq.conf to change DHCP settings.

- **Web Server:** Update captive_portal.py and the HTML template as needed.