#!/bin/bash
set -e
echo "on-create.sh script started"

# Ensure script/setup is executable
chmod +x script/setup

# Run the main setup script
script/setup

echo "on-create.sh script finished"
