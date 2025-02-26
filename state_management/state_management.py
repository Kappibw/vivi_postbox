#!/usr/bin/env python3
"""
state_management.py - Helper module for managing shared state via a JSON file.

This module provides functions to read, write, and clear a JSON state file.
The state file is stored in the same directory as this module.
"""

import os
import json

# Define the path to the state.json file relative to this module
STATE_FILE = os.path.join(os.path.dirname(os.path.realpath(__file__)), "state.json")


def read_state():
    """
    Read and return the current state from the state.json file.
    Returns an empty dictionary if the file does not exist or is empty.
    """
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r") as f:
            state = json.load(f)
        return state
    except Exception as e:
        print("Error reading state file:", e)
        return {}


def write_state(state):
    """
    Write the provided state dictionary to the state.json file.

    Args:
        state (dict): The state to write.
    """
    try:
        with open(STATE_FILE, "w") as f:
            json.dump(state, f, indent=4)
        print("State updated:", state)
    except Exception as e:
        print("Error writing state file:", e)


def clear_state():
    """
    Clear the state by writing an empty dictionary to the state.json file.
    """
    write_state({})


if __name__ == "__main__":
    # Simple test of the module
    print("Initial state:", read_state())
    new_state = {"message_pending": True, "mp3_path": "downloads/message.mp3"}
    write_state(new_state)
    print("Updated state:", read_state())
    clear_state()
    print("State after clearing:", read_state())
