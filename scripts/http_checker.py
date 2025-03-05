#!/usr/bin/env python3
"""
HTTP Checker Script

- Periodically polls an HTTP endpoint.
- Downloads an MP3 file when a specific response is detected.
"""

import os
import time
import requests
from state_management.state_management import read_state, write_state
import sys

# Configuration
POLL_INTERVAL_SECONDS = 10  # how often to poll the endpoint
PENDING_SLEEP_SECONDS = 1 # how long to wait for pending message to be cleared.
GET_POST_ENDPOINT = "https://api.thinkkappi.com/vivi/get_post"
DOWNLOAD_DIR = "/home/pi/mp3_downloads"  # change as needed

def download_mp3(mp3_url):
    """Downloads the MP3 file from the given URL and returns the local file path."""
    try:
        # Create download directory if it doesn't exist
        if not os.path.exists(DOWNLOAD_DIR):
            os.makedirs(DOWNLOAD_DIR)
        
        # Use the last part of the URL as the filename
        filename = os.path.basename(mp3_url)
        local_path = os.path.join(DOWNLOAD_DIR, filename)

        # Stream the download and write to file
        response = requests.get(mp3_url, stream=True)
        response.raise_for_status()  # Raise an exception for HTTP errors
        with open(local_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        print(f"Downloaded MP3 to {local_path}")
        return local_path
    except Exception as e:
        print(f"Failed to download MP3 from {mp3_url}: {e}")
        return None

def poll_endpoint():
    """Polls the HTTP endpoint and processes the response."""
    try:
        response = requests.get(GET_POST_ENDPOINT)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"Error fetching data from {GET_POST_ENDPOINT}: {e}")
        return

    msg_type = data.get("type")
    mp3_url = data.get("mp3_url")
    msg_id = data.get("id")
    
    if mp3_url:
        # Download the MP3
        local_mp3_path = download_mp3(mp3_url)
        if local_mp3_path:
            # Update state to set message pending and store mp3 path
            current_state = read_state()
            current_state["message_pending"] = True
            current_state["mp3_path"] = local_mp3_path
            current_state["message_id"] = msg_id
            write_state(current_state)
            print("State updated: message pending set to True and mp3 path saved.")
    else:
        print(f"Received non-audio message or missing mp3_url. Type: {msg_type}, id: {msg_id}")

def mark_message_listened():
    current_state = read_state()
    message_id = current_state.get("message_id", "")
    current_state["message_listened"] = False
    write_state(current_state)
    if not message_id:
        print("No message ID found")
        return
    print(f"Marking message {message_id} listened")
    
    # Build the URL for the DELETE request
    url = f"https://api.thinkkappi.com/vivi/delete_post/{message_id}"
    
    try:
        response = requests.delete(url)
        if response.status_code == 200:
            print(f"Message {message_id} deleted successfully.")
        else:
            print(f"Failed to delete message {message_id}: {response.text}")
    except Exception as e:
        print(f"Error calling delete endpoint: {e}")


def main():
    print("Starting HTTP Checker...")
    while True:
        sys.stdout.flush()
        current_state = read_state()
        pending_message = current_state.get("message_pending", False)
        if pending_message:
            time.sleep(PENDING_SLEEP_SECONDS)
            continue
        message_listened = current_state.get("message_listened", False)
        if message_listened:
            mark_message_listened()
        poll_endpoint()
        time.sleep(POLL_INTERVAL_SECONDS)

if __name__ == "__main__":
    main()
