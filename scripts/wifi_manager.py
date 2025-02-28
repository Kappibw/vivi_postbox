#!/usr/bin/python3 -u
"""
WiFi Manager with Captive Portal Activation

This script continuously monitors connectivity to a known host. If no connectivity
is detected for 5 minutes, it launches the captive portal by running the installation
script (which configures hostapd, dnsmasq, and starts the captive portal web server).

Once connectivity is restored (or after the user has submitted new WiFi credentials),
the script stops the captive portal mode.
"""

import os
import subprocess
import time
import sys
from state_management.state_management import read_state, write_state

# The host to ping to check connectivity (Google DNS is commonly used)
PING_HOST = "8.8.8.8"
# How many seconds to wait between checks
CHECK_INTERVAL = 10
# How many seconds of consecutive connectivity loss trigger captive portal mode
TIMEOUT = 30

# Calculate the relative path to the captive portal install script
CURRENT_DIR = os.path.dirname(os.path.realpath(__file__))
CAPTIVE_PORTAL_INSTALL_SCRIPT = os.path.join(CURRENT_DIR, "..", "captive_portal", "install_captive_portal.sh")


def is_connected(host=PING_HOST):
    """
    Returns True if the system can ping the host successfully, else False.
    """
    try:
        # '-c 1' sends a single ping packet
        result = subprocess.run(
            ["ping", "-c", "1", host],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception as e:
        print("Error during ping:", e)
        return False


def start_captive_portal():
    """
    Launch the captive portal by running the install script.
    This script should set up hostapd, dnsmasq, and start the captive portal web server.
    """
    print("Starting captive portal mode...")
    try:
        subprocess.run(["/bin/bash", CAPTIVE_PORTAL_INSTALL_SCRIPT], check=True)
    except subprocess.CalledProcessError as e:
        print("Failed to start captive portal:", e)


def stop_captive_portal():
    """
    Stop the captive portal services.
    This function kills the captive portal web server.
    """
    print("Stopping captive portal server...")
    try:
        # Kill the captive portal web server process
        subprocess.run(["pkill", "-f", "captive_portal.py"])
    except subprocess.CalledProcessError as e:
        print("Failed to stop captive portal:", e)


def main():
    disconnect_time = 0
    portal_active = False

    while True:
        state = read_state()
        if is_connected():
            state["wifi_not_connected"] = False
            write_state(state)
            print("Internet connectivity is present.")
            disconnect_time = 0
            if portal_active:
                # Connectivity restored; disable captive portal mode.
                stop_captive_portal()
                portal_active = False
        else:
            state["wifi_not_connected"] = True
            write_state(state)
            disconnect_time += CHECK_INTERVAL
            print(f"Connectivity lost for {disconnect_time} seconds.")
            if disconnect_time >= TIMEOUT and not portal_active:
                start_captive_portal()
                portal_active = True
        time.sleep(CHECK_INTERVAL)
        sys.stdout.flush()


if __name__ == "__main__":
    main()
