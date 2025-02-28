#!/usr/bin/env python3 -u
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
import sys

# Configure the GPIO pin connected to the Hall Effect sensor.
HALL_PIN = 17
hall_sensor = Button(HALL_PIN, pull_up=True)

def play_mp3(filepath):
    print(f"Playing MP3: {filepath}")
    process = subprocess.Popen(["mpg321", "-o", "alsa", "-a", "plughw:2,0", "-g", "200", filepath])
    try:
        # Wait for mpg321 to finish normally
        process.wait()
    except KeyboardInterrupt:
        print("KeyboardInterrupt caught; terminating mpg321.")
        process.terminate()  # Send SIGTERM
        process.wait()       # Wait for it to exit
        raise  # Re-raise to let the top-level code handle clean shutdown

def cleanup_mp3():
    """
    Loads the current state, deletes the MP3 file specified in the state, 
    and resets the mp3_path and message_pending flag.
    """
    current_state = read_state()
    mp3_path = current_state.get("mp3_path", "")
    
    if mp3_path and os.path.exists(mp3_path):
        try:
            os.remove(mp3_path)
            print(f"Deleted MP3 file at {mp3_path}")
        except Exception as e:
            print(f"Error deleting MP3 file: {e}")
    else:
        print("No MP3 file found for cleanup.")


def main():
    print("Audio player started. Waiting for pending message and sensor trigger.")
    while True:
        state = read_state()
        sys.stdout.flush()
        # Check if there is a pending message and we are not already playing.
        if state and state.get("message_pending") and not state.get("playing"):
            # Wait for the sensor to be triggered.
            if hall_sensor.is_pressed:
                print("Hall sensor triggered.\n\n")
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
                    new_state["message_listened"] = True
                    write_state(new_state)
                    print("Playback finished; state updated.")
                    # Delete mp3 file
                    cleanup_mp3()
                    # Small pause to allow state change to propagate.
                    time.sleep(1)
        # Poll every 0.1 seconds.
        time.sleep(0.1)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Audio player interrupted. Exiting.")
