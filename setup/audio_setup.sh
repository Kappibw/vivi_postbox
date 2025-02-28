#!/bin/bash
# audio_setup.sh
# This script sets up the Raspberry Pi for I2S audio output through the MAX98357.
# It does the following:
# 1. Installs mpg321 if it is not already installed.
# 2. Ensures the I2S interface is enabled.
# 3. Adds an ALSA configuration file to set the default output device to the I2S DAC.
# 4. Provides instructions to reboot if necessary.

# --- Step 0: Install mpg321 if not already installed ---
if ! command -v mpg321 >/dev/null 2>&1; then
    echo "mpg321 not found. Installing mpg321..."
    sudo apt-get update
    sudo apt-get install -y mpg321
else
    echo "mpg321 is already installed."
fi

# --- Step 1: Enable I2S interface ---
# On Raspberry Pi OS, the I2S interface is usually enabled by default if you use
# an appropriate dtoverlay. If not, edit /boot/config.txt and add the following line:
#
#   dtoverlay=hifiberry-dac
#
# or for the MAX98357 you might try:
#
#   dtoverlay=googlevoicehat-soundcard
#
# (There isn't an official overlay for MAX98357, but many users find that the
# hifiberry-dac or similar overlays work, or you can use a custom overlay.)
#
# Check if /boot/firmware/config.txt already contains an I2S overlay. If not, append one.
CONFIG_FILE="/boot/firmware/config.txt"
OVERLAY_LINE="dtoverlay=googlevoicehat-soundcard"
I2S_LINE="dtparam=i2s=on"

if ! grep -q "$OVERLAY_LINE" "$CONFIG_FILE"; then
    echo "Enabling I2S audio overlay in $CONFIG_FILE"
    echo "" >> "$CONFIG_FILE"
    echo "# Enable I2S audio output for MAX98357" >> "$CONFIG_FILE"
    echo "$OVERLAY_LINE" >> "$CONFIG_FILE"
else
    echo "I2S overlay already enabled in $CONFIG_FILE"
fi

# Handle the I2S parameter
if grep -q "^[#]*\s*$I2S_LINE" "$CONFIG_FILE"; then
    echo "Uncommenting I2S parameter in $CONFIG_FILE"
    sed -i "s|^[#]*\s*$I2S_LINE|$I2S_LINE|" "$CONFIG_FILE"
elif ! grep -q "^$I2S_LINE$" "$CONFIG_FILE"; then
    echo "Enabling I2S parameter in $CONFIG_FILE"
    echo "$I2S_LINE" >> "$CONFIG_FILE"
else
    echo "I2S parameter already enabled in $CONFIG_FILE"
fi

# --- Step 2: Configure ALSA ---
# Create or update /etc/asound.conf so that the default ALSA device points to the I2S DAC.
# This file configures ALSA to use the MAX98357 as the default soundcard.
ASOUND_CONF="/etc/asound.conf"
sudo tee "$ASOUND_CONF" > /dev/null <<EOF
pcm.!default {
    type plug
    slave {
        pcm "hw:2,0"
        rate 44100
        format S16_LE
        channels 2
    }
}

ctl.!default {
    type hw
    card 2
}
EOF
echo "ALSA configured to use card 2 as default in $ASOUND_CONF"

# Note: Depending on your setup, the MAX98357 might not be card 2.
# You can check the output of 'aplay -l' to determine the correct card number.
#
# If you need to set a different card, adjust the card number in the asound.conf file.

# --- Step 3: Restart the audio service or reboot ---
echo "Audio setup complete."
echo "Please reboot the Pi for all changes to take effect, if you haven't already."
echo "You can reboot now by running: sudo reboot"
