#!/usr/bin/env python3 -u
"""
LED Display Script with Full-Cycle Pulsing and Smooth Interrupt Transitions

- Reads the state from the shared state_management module.
- If no pending message: turns LEDs off.
- If a pending message exists: displays a gentle pulsing, multicolored light (256 steps).
- If a message is playing: displays a more active pulsing pattern (fewer, bigger steps).
- If a pulse cycle is interrupted, the current LED colors smoothly fade out.
"""

import time
import math
import random
from state_management.state_management import read_state, write_state
import sys

sys.path.append("/home/pi/git/vivi_postbox/venv/lib/python3.11/site-packages")

# Try to import the rpi_ws281x library. If not available (e.g. on macOS), define dummy functions.
try:
    from rpi_ws281x import PixelStrip, Color
except Exception as e:
    print(f"FAILED to import rpi_ws281x: {type(e).__name__}: {e}")
    print("Using dummy LED functions...")

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
LED_COUNT = 12  # Number of LED pixels.
LED_PIN = 12  # GPIO pin connected to the pixels (must support PWM!)
LED_BRIGHTNESS = 200  # Brightness (0 to 255)

# Initialize the LED strip
strip = PixelStrip(LED_COUNT, LED_PIN, brightness=LED_BRIGHTNESS)
strip.begin()


def led_off():
    """Turn all LEDs off."""
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()


def fade_out(current_colors, steps=10, delay=0.02):
    """
    Gradually dim the current LED colors to off.

    Args:
        current_colors (list): List of (r, g, b) tuples representing the current colors.
        steps (int): Number of steps to use in the fade.
        delay (float): Delay (in seconds) between fade steps.
    """
    for step in range(steps):
        factor = (steps - step - 1) / (steps - 1)  # factor goes from 1.0 to 0.0
        for i, (r, g, b) in enumerate(current_colors):
            new_r = int(r * factor)
            new_g = int(g * factor)
            new_b = int(b * factor)
            strip.setPixelColor(i, Color(new_r, new_g, new_b))
        strip.show()
        time.sleep(delay)
    led_off()


def gentle_pulse():
    """
    Displays a gentle chasing color effect on a 12 LED ring.
    The hue (pink to purple to pink) appears to chase around the ring,
    while all LEDs pulse in unison from dim (0) to bright (255) and back to dim,
    over 256 steps.
    """
    for j in range(256):
        # Global brightness for all LEDs using a sine wave (0->max->0)
        angle = j * (2 * math.pi / 256) - math.pi / 2  # maps j to [-pi/2, 3pi/2]
        brightness = int((math.sin(angle) + 1) * 127.5)  # brightness goes from 0 to 255 to 0

        current_colors = []
        for i in range(LED_COUNT):
            # Offset each LED's color phase to create a chasing effect
            offset = int((256 / LED_COUNT) * i)
            phase = (j + offset) % 256

            # Interpolate blue channel: pink (blue = 0.5*brightness) to purple (blue = brightness)
            t = (math.sin(phase * (2 * math.pi / 256)) + 1) / 2
            red = brightness
            green = 0
            blue = int(brightness * (0.5 + 0.5 * t))
            current_colors.append((red, green, blue))
            strip.setPixelColor(i, Color(red, green, blue))

        strip.show()
        time.sleep(0.02)

        # Check for state changes; if detected, fade out current colors and exit cycle
        state = read_state()
        if not state or not state.get("message_pending"):
            fade_out(current_colors)
            return
        if state.get("playing"):
            fade_out(current_colors)
            return


def active_pulse():
    """
    Displays a visualizer-style active pattern while a message is playing.
    Each cycle randomly either does:
      - A "pulse": the LEDs smoothly fade in and out over a random duration between 0.1 and 0.5 seconds.
      - A "blink": the LEDs instantly turn on (full brightness) for a random duration (0.1-0.5 sec) then off.
    Random base colors are chosen for each cycle.
    The function runs until the 'playing' state is no longer True.
    """
    while True:
        # Check current state; if not playing, fade out and exit.
        state = read_state()
        if not state or not state.get("playing"):
            fade_out([(0, 0, 0)] * LED_COUNT)
            return

        # Randomly choose between a pulse or a blink.
        mode = random.choice(["pulse", "blink"])

        # Generate random base colors for each LED.
        base_colors = []
        for i in range(LED_COUNT):
            r = random.randint(0, 255)
            g = random.randint(0, 255)
            b = random.randint(0, 255)
            base_colors.append((r, g, b))

        if mode == "pulse":
            # Pulse mode: smooth fade in then fade out.
            duration = random.uniform(0.1, 0.5)  # total pulse duration
            steps = 30  # fixed number of steps for smooth transition
            delay = duration / steps

            # For a smooth pulse, we use sine modulation from 0 to pi (0 -> 1 -> 0).
            current_colors = []
            for j in range(steps + 1):
                angle = j * math.pi / steps  # angle in [0, pi]
                brightness_factor = math.sin(angle)

                current_colors = []
                for i in range(LED_COUNT):
                    r, g, b = base_colors[i]
                    new_r = int(r * brightness_factor)
                    new_g = int(g * brightness_factor)
                    new_b = int(b * brightness_factor)
                    current_colors.append((new_r, new_g, new_b))
                    strip.setPixelColor(i, Color(new_r, new_g, new_b))
                strip.show()
                time.sleep(delay)

                # Check for state changes during the pulse cycle.
                state = read_state()
                if not state or not state.get("playing"):
                    fade_out(current_colors)
                    return
        else:
            # Blink mode: instant on full brightness for a short random duration, then off.
            on_duration = random.uniform(0.1, 0.5)
            # Turn all LEDs to their base (full brightness) color.
            for i in range(LED_COUNT):
                r, g, b = base_colors[i]
                strip.setPixelColor(i, Color(r, g, b))
            strip.show()
            time.sleep(on_duration)

            # Turn off LEDs.
            for i in range(LED_COUNT):
                strip.setPixelColor(i, Color(0, 0, 0))
            strip.show()
            # Short off interval before the next cycle.
            time.sleep(0.05)


def wifi_not_connected():
    """
    Sets all LEDs to green at maximum brightness (0,255,0) for one second, then returns.
    """
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 255, 0))
    strip.show()
    time.sleep(1)


def nightlight():
    """
    Sets all LEDs to amber (255, 220, 80) to act as a nightlight.
    """
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(255, 220, 80))
    strip.show()
    time.sleep(1)


def orange_blink(current_state):
    """
    Blinks all LEDs bright orange three times within 0.8 seconds.
    Each blink is on for 0.2 seconds, with 0.1 seconds off between blinks.
    """
    orange = Color(255, 165, 0)  # Bright orange
    for i in range(3):
        # Turn all LEDs orange.
        for j in range(LED_COUNT):
            strip.setPixelColor(j, orange)
        strip.show()
        time.sleep(0.1)

        # Turn LEDs off between blinks (except after the last blink)
        for j in range(LED_COUNT):
            strip.setPixelColor(j, Color(0, 0, 0))
        strip.show()
        time.sleep(0.1)
    current_state["user_input"] = False
    write_state(current_state)


def main():
    """
    Main loop: periodically checks the shared state and updates the LED pattern accordingly.
    """
    while True:
        state = read_state()
        if not state:
            led_off()
            time.sleep(0.5)
            continue
        if state.get("wifi_not_connected"):
            wifi_not_connected()
            continue
        if state.get("nightlight_on"):
            nightlight()
            continue
        if not state.get("message_pending") and state.get("user_input"):
            orange_blink(state)
        elif state.get("message_pending") and state.get("playing"):
            active_pulse()
        elif state.get("message_pending"):
            gentle_pulse()
        else:
            led_off()
            time.sleep(0.5)
        sys.stdout.flush()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        led_off()
        print("LED display interrupted and turned off.")
