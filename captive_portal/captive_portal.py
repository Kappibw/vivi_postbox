#!/usr/bin/env python3
"""
Captive Portal Web Server

This script serves a simple HTML form where users can enter new WiFi credentials.
It then updates the wpa_supplicant configuration, calls a shell script to revert the Pi 
from captive portal (AP mode) to client mode, reconfigures the WiFi interface, and checks
for connectivity, finally informing the user whether the connection was successful.
"""

import os
import subprocess
import time
import sys
import logging
from flask import Flask, render_template, request, redirect, url_for

# Create a logger for the application
logger = logging.getLogger('captive_portal')
logger.setLevel(logging.DEBUG)

# Create handlers: one for file, one for console (if desired)
file_handler = logging.FileHandler('/var/log/captive_portal.log')
file_handler.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()

# Create a logging format and add it to the handlers
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# Add handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)

# Now create the Flask app and attach the logger
app = Flask(__name__)
app.logger.handlers = []  # Remove default handlers
app.logger.propagate = True  # Ensure logs propagate to our logger
app.logger.addHandler(file_handler)
app.logger.setLevel(logging.DEBUG)
logger.debug("Custom logger initialized.")

# The path to the shell script that reverts AP mode to client mode
REVERT_SCRIPT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "revert_captive_portal.sh")
CAPTIVE_PORTAL_SCRIPT = os.path.join(os.path.dirname(os.path.realpath(__file__)), "install_captive_portal.sh")


def revert_to_client_mode():
    """
    Revert the Pi from captive portal (AP mode) to normal client mode by running
    an external shell script.
    """
    try:
        subprocess.run(["/bin/bash", REVERT_SCRIPT], check=True)
        app.logger.info("Reverted to client mode using the shell script.")
    except Exception as e:
        app.logger.error("Error reverting to client mode:", e)
        raise e

def open_captive_portal():
    """
    Open the captive portal again for retries.
    """
    try:
        subprocess.run(["/bin/bash", CAPTIVE_PORTAL_SCRIPT], check=True)
        app.logger.info("Opened captive portal using script.")
    except Exception as e:
        app.logger.error("Error opening captive portal:", e)
        raise e

def update_nm_connection(ssid, password):
    """
    Update the NetworkManager connection for the given SSID with the new password.
    If the connection already exists, modify it; otherwise, create a new connection.
    """
    try:
        # Check if the connection already exists:
        result = subprocess.run(["nmcli", "-f", "NAME", "connection", "show"], capture_output=True, text=True)
        connections = result.stdout.splitlines()

        env = os.environ.copy()
        # Ensure PATH is set correctly
        env["PATH"] = "/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

        try:
            subprocess.run(["nmcli", "connection", "delete", ssid], check=True, env=env)
            app.logger.info(f"Removed old connection to {ssid}.")
        except Exception as e:
            app.logger.warning("Didn't remove an existing connection")

        time.sleep(4)
        # Create a new connection
        result = subprocess.run(
            ["/usr/bin/nmcli", "device", "wifi", "connect", ssid, "password", password],
            check=False, capture_output=True, text=True,  env=env
        )
        app.logger.info(f"nmcli stdout: {result.stdout}")
        app.logger.error(f"nmcli stderr: {result.stderr}")
        if result.returncode != 0:
            raise Exception(f"nmcli returned non-zero exit code {result.returncode}")
        app.logger.info(f"Created new NetworkManager profile for {ssid}.")
    except Exception as e:
        app.logger.error("Error updating NetworkManager connection:", exc_info=e)
        open_captive_portal()
        app.logger.info("Opened Captive Portal again")
        raise e


def test_connectivity():
    """
    Wait a few seconds for the WiFi to reconnect, then test connectivity by pinging 8.8.8.8.
    Returns True if successful, False otherwise.
    """
    time.sleep(5)
    app.logger.info("Waited for recconect, testing connection.")
    try:
        result = subprocess.run(
            ["ping", "-c", "1", "8.8.8.8"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return result.returncode == 0
    except Exception as e:
        app.logger.error("Error during connectivity test:", e)
        return False


def update_and_connect(ssid, password):
    """
    Update the WiFi credentials, revert from AP mode to client mode,
    trigger reconfiguration, and test connectivity.
    Returns "success" if connected, "fail" otherwise.
    """
    try:
        revert_to_client_mode()
        update_nm_connection(ssid, password)
        if test_connectivity():
            return "success"
        else:
            return "fail"
    except Exception as e:
        app.logger.error("Exception during update and connect:", e)
        return "fail"


@app.route("/", methods=["GET", "POST"])
def portal():
    print("request received", flush=True)
    app.logger.info("Received a request to / with method: %s", request.method)
    if request.method == "POST":
        print("POST received", flush=True)
        ssid = request.form.get("ssid")
        password = request.form.get("password")
        app.logger.info(f"Received new credentials: SSID={ssid}, Password={password}")
        outcome = update_and_connect(ssid, password)
        app.logger.info(f"Result is {outcome}")
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


# Catch-all error handler: if a requested URL isn't found, serve the portal page.
@app.errorhandler(404)
def page_not_found(e):
    return render_template("portal.html"), 200


if __name__ == "__main__":
    app.logger.info("Captive portal app has begun!!")
    app.run(host="0.0.0.0", port=80)
