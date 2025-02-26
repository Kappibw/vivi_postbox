#!/usr/bin/env python3
"""
Captive Portal Web Server

This script serves a simple HTML form where users can enter new WiFi credentials.
It then updates the wpa_supplicant configuration, reconfigures the WiFi interface,
and checks for connectivity, finally informing the user whether the connection was successful.
"""

import os
import subprocess
import time
from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

WPA_SUPPLICANT_CONF = "/etc/wpa_supplicant/wpa_supplicant.conf"
WPA_BACKUP_CONF = "/etc/wpa_supplicant/wpa_supplicant.conf.bak"


def update_wpa_supplicant(ssid, password):
    """
    Backup the current configuration and overwrite wpa_supplicant.conf
    with a new configuration that contains the provided SSID and password.
    """
    try:
        # Backup the existing configuration
        subprocess.run(["cp", WPA_SUPPLICANT_CONF, WPA_BACKUP_CONF], check=True)
    except Exception as e:
        print("Warning: Could not backup wpa_supplicant configuration:", e)

    # Create a new configuration. Adjust the country code as needed.
    config = f"""ctrl_interface=DIR=/var/run/wpa_supplicant GROUP=netdev
update_config=1
country=US

network={{
    ssid="{ssid}"
    psk="{password}"
}}
"""
    try:
        with open(WPA_SUPPLICANT_CONF, "w") as f:
            f.write(config)
        print("wpa_supplicant configuration updated.")
    except Exception as e:
        print("Error writing wpa_supplicant configuration:", e)
        raise e


def reconfigure_wifi():
    """
    Reconfigure the WiFi interface so that the new credentials take effect.
    """
    try:
        # Use wpa_cli to trigger reconfiguration on interface wlan0
        subprocess.run(["wpa_cli", "-i", "wlan0", "reconfigure"], check=True)
        print("WiFi reconfiguration triggered.")
    except Exception as e:
        print("Error reconfiguring WiFi:", e)
        raise e


def test_connectivity():
    """
    Wait a few seconds for the WiFi to reconnect, then test connectivity by pinging a known host.
    Returns True if successful, False otherwise.
    """
    # Give the interface time to reconnect (adjust the sleep time as needed)
    time.sleep(20)
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "8.8.8.8"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception as e:
        print("Error during connectivity test:", e)
        return False


def update_and_connect(ssid, password):
    """
    Update the WiFi credentials, trigger reconfiguration, and test connectivity.
    Returns "success" if connected, "fail" otherwise.
    """
    try:
        update_wpa_supplicant(ssid, password)
        reconfigure_wifi()
        if test_connectivity():
            return "success"
        else:
            return "fail"
    except Exception as e:
        print("Exception during update and connect:", e)
        return "fail"


@app.route("/", methods=["GET", "POST"])
def portal():
    if request.method == "POST":
        ssid = request.form.get("ssid")
        password = request.form.get("password")
        print(f"Received new credentials: SSID={ssid}, Password={password}")
        outcome = update_and_connect(ssid, password)
        return redirect(url_for("result", outcome=outcome))
    return render_template("portal.html")


@app.route("/result")
def result():
    outcome = request.args.get("outcome", "fail")
    if outcome == "success":
        message = "Connection successful! The Pi is now connected to the new WiFi network."
    else:
        message = "Connection failed. Please check your credentials and try again."
    return f"<h3>{message}</h3>"


if __name__ == "__main__":
    # Run on all interfaces; port 80 requires root privileges
    app.run(host="0.0.0.0", port=80)
