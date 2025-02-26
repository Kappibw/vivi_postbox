#!/usr/bin/env python3
"""
Audio Player Script

This script continuously monitors the shared state and the Hall Effect sensor.
When a pending message exists and the sensor is triggered, it:
1) Sets the 'playing' state to True.
2) Plays the MP3 from the filepath in the state using a command-line MP3 player.
3) Once playback finishes, sets 'playing' and 'message_pending' to False.
"""

import time
import subprocess
from gpiozero import Button
from state_management.state_management import read_state, write_state

# Configure the GPIO pin connected to the Hall Effect sensor.
HALL_PIN = 17
hall_sensor = Button(HALL_PIN, pull_up=True)


# Define a helper to play the MP3 using a command-line player.
# Ensure that 'mpg123' is installed on your Raspberry Pi:
#   sudo apt-get install mpg123
def play_mp3(filepath):
    try:
        print(f"Playing MP3: {filepath}")
        subprocess.run(["mpg123", filepath], check=True)
    except subprocess.CalledProcessError as e:
        print("Error playing mp3:", e)


def main():
    print("Audio player started. Waiting for pending message and sensor trigger.")
    while True:
        state = read_state()
        # Check if there is a pending message and we are not already playing.
        if state and state.get("message_pending") and not state.get("playing"):
            # Wait for the sensor to be triggered.
            if hall_sensor.is_pressed:
                print("Hall sensor triggered.")
                mp3_path = state.get("mp3_path")
                if not mp3_path:
                    print("No MP3 filepath found in state; skipping playback.")
                else:
                    # Update state to indicate playback is starting.
                    new_state = state.copy()
                    new_state["playing"] = True
                    write_state(new_state)

                    # Play the MP3.
                    play_mp3(mp3_path)

                    # After playback, update the state to clear pending and playing flags.
                    new_state["playing"] = False
                    new_state["message_pending"] = False
                    write_state(new_state)
                    print("Playback finished; state updated.")
                    # Small pause to allow state change to propagate.
                    time.sleep(1)
        # Poll every 0.1 seconds.
        time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Audio player interrupted. Exiting.")
