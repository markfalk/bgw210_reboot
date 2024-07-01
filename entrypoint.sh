#!/bin/sh

# Check if PASSWORD is set
if [ -z "$PASSWORD" ]; then
  echo "The PASSWORD environment variable is not set."
  exit 1
fi

# Run the Python script
python bgw210_reboot.py
