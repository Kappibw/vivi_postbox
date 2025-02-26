#!/usr/bin/env python3
"""
Captive Portal Web Server

This script serves a simple HTML form where users can enter new WiFi credentials.
"""

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)


@app.route("/", methods=["GET", "POST"])
def portal():
    if request.method == "POST":
        ssid = request.form.get("ssid")
        password = request.form.get("password")
        # TODO: Save credentials and update wpa_supplicant configuration
        # For now, just print them.
        print(f"Received new credentials: SSID={ssid}, Password={password}")
        # Optionally, trigger a script to switch from AP mode to client mode.
        return redirect(url_for("success"))
    return render_template("portal.html")


@app.route("/success")
def success():
    return "<h3>Credentials received. The Pi will now attempt to connect to the new WiFi network.</h3>"


if __name__ == "__main__":
    # Run on all interfaces; port 80 may require sudo privileges
    app.run(host="0.0.0.0", port=80)
