#!/bin/bash
# Stop the script if any command fails
set -e 

cd /home/opc/Abdulaziz-portfilio

# Force the instance to match GitHub exactly
git fetch origin
git reset --hard origin/main

# Rebuild with the new changes
docker compose up --build -d

# Clean up old images to save OCI disk space
docker image prune -f