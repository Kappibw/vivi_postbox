#!/usr/bin/env python3
"""
LED Display Script

- Reads the state from the shared state_management module.
- If no pending message: turns LEDs off.
- If pending message exists: displays a gentle pulsing, multicolored light.
- If a message is playing: displays a more active pulsing pattern.
"""

import time
import math
from state_management.state_management import read_state

# Try to import the rpi_ws281x library. If not available (e.g. on macOS), define dummy functions.
try:
    from rpi_ws281x import PixelStrip, Color
except ImportError:
    print("rpi_ws281x library not found. Using dummy LED functions for development.")

    class PixelStrip:
        def __init__(self, num, pin, freq_hz=800000, dma=10, invert=False, brightness=255, channel=0):
            self.num = num

        def begin(self):
            pass

        def show(self):
            pass

        def setPixelColor(self, i, color):
            pass

    def Color(r, g, b):
        return (r, g, b)


# LED configuration
LED_COUNT = 16  # Number of LED pixels.
LED_PIN = 18  # GPIO pin connected to the pixels (must support PWM!)
LED_BRIGHTNESS = 50  # Brightness (0 to 255)

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, brightness=LED_BRIGHTNESS)
strip.begin()


def led_off():
    """Turn all LEDs off."""
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


def gentle_pulse():
    """
    Display a gentle pulsing multicolored light.
    The function runs in a cycle but checks the state to allow interruption if needed.
    """
    for j in range(256):  # One cycle of the sine wave
        # Calculate a brightness value that oscillates between 0 and 255
        brightness = int((math.sin(j * math.pi / 256) + 1) * 127.5)
        for i in range(LED_COUNT):
            # Create a color pattern that shifts per LED: cycle through red, green, blue
            if i % 3 == 0:
                r, g, b = brightness, 0, 0
            elif i % 3 == 1:
                r, g, b = 0, brightness, 0
            else:
                r, g, b = 0, 0, brightness
            strip.setPixelColor(i, Color(r, g, b))
        strip.show()
        time.sleep(0.02)
        # Check state frequently; exit if no longer pending or if playing state has changed
        state = read_state()
        if not state or not state.get("message_pending"):
            return
        if state.get("playing"):
            return


def active_pulse():
    """
    Display a more active pulsing pattern while the message is playing.
    Uses a faster pulsation effect.
    """
    for j in range(256):
        # Faster sine wave oscillation for a more vigorous effect
        brightness = int((math.sin(j * math.pi / 128) + 1) * 127.5)
        for i in range(LED_COUNT):
            # For active state, we'll use a constant color (e.g., blue) for all LEDs.
            r, g, b = 0, 0, brightness
            strip.setPixelColor(i, Color(r, g, b))
        strip.show()
        time.sleep(0.01)
        state = read_state()
        # Exit the active pulse cycle if 'playing' flag is cleared
        if not state or not state.get("playing"):
            return


def main():
    """
    Main loop: periodically check the shared state and update the LED pattern accordingly.
    """
    while True:
        state = read_state()
        if not state or not state.get("message_pending"):
            # No pending messages: ensure LEDs are off
            led_off()
            time.sleep(1)
        elif state.get("playing"):
            # If playing, show an active pulse pattern
            active_pulse()
        else:
            # Otherwise, if there's a pending message, show a gentle pulse pattern
            gentle_pulse()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        led_off()
        print("LED display interrupted and turned off.")
