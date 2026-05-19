#!/bin/bash
# Usage: ./ops/server-status.sh <user@host> <app-name>
# Example: ./ops/server-status.sh root@95.217.153.143 enjoythenews

HOST=$1
APP=$2

if [ -z "$HOST" ] || [ -z "$APP" ]; then
    echo "Usage: $0 <user@host> <app-name>"
    exit 1
fi

ssh "$HOST" bash << EOF
echo "=== Service status ==="
systemctl status $APP --no-pager

echo ""
echo "=== Last 20 log lines ==="
journalctl -u $APP -n 20 --no-pager
EOF
