#!/bin/bash
# install_services.sh
# This script copies the systemd service files from the repository's services/
# directory to /etc/systemd/system, reloads systemd, enables, and starts them.

# Ensure the script is run as root
if [ "$(id -u)" -ne 0 ]; then
  echo "This script must be run as root. Please run with sudo."
  exit 1
fi

# Determine the absolute path to this script's directory
SERVICE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TARGET_DIR="/etc/systemd/system"

# List service files in the current directory (modify if needed)
SERVICE_FILES=("wifi_manager.service" "http_checker.service" "led_audio.service")

echo "Installing systemd service files..."

for service in "${SERVICE_FILES[@]}"; do
  if [ -f "${SERVICE_DIR}/${service}" ]; then
    cp "${SERVICE_DIR}/${service}" "${TARGET_DIR}/"
    echo "Copied ${service} to ${TARGET_DIR}"
  else
    echo "Warning: ${service} not found in ${SERVICE_DIR}"
  fi
done

echo "Reloading systemd daemon..."
systemctl daemon-reload

echo "Enabling and starting services..."
for service in "${SERVICE_FILES[@]}"; do
  systemctl enable "${service}"
  systemctl start "${service}"
  echo "Enabled and started ${service}"
done

echo "Service installation complete. You can check service status using:"
echo "  systemctl status wifi_manager.service"
echo "  systemctl status http_checker.service"
echo "  systemctl status led_audio.service"
