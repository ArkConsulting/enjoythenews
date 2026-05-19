#!/bin/bash
# Usage: ./ops/deploy.sh <user@host> <app-name>
# Example: ./ops/deploy.sh root@95.217.153.143 enjoythenews

set -e

HOST=$1
APP=$2

if [ -z "$HOST" ] || [ -z "$APP" ]; then
    echo "Usage: $0 <user@host> <app-name>"
    exit 1
fi

echo "==> Deploying $APP to $HOST"

ssh "$HOST" bash << EOF
set -e

cd /app/$APP

echo "--- Pulling latest code ---"
git pull

echo "--- Updating dependencies ---"
.venv/bin/pip install -q -r requirements.txt

echo "--- Restarting service ---"
systemctl restart $APP

echo "--- Status ---"
systemctl is-active $APP && echo "$APP is running" || echo "$APP failed to start"
EOF

echo "==> Deploy complete."
