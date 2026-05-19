#!/bin/bash
# Usage: ./ops/server-setup.sh <user@host> <github-repo> <app-name> <port>
# Example: ./ops/server-setup.sh root@95.217.153.143 ArkConsulting/enjoythenews enjoythenews 8765

set -e

HOST=$1
REPO=$2
APP=$3
PORT=$4

if [ -z "$HOST" ] || [ -z "$REPO" ] || [ -z "$APP" ] || [ -z "$PORT" ]; then
    echo "Usage: $0 <user@host> <github-repo> <app-name> <port>"
    exit 1
fi

echo "==> Setting up $APP on $HOST"

ssh "$HOST" bash << EOF
set -e

echo "--- Installing system packages ---"
apt-get update -qq
apt-get install -y -qq python3 python3-pip python3-venv git nginx certbot python3-certbot-nginx

echo "--- Cloning repository ---"
mkdir -p /app
cd /app
git clone https://github.com/$REPO.git $APP
cd $APP

echo "--- Setting up Python environment ---"
python3 -m venv .venv
.venv/bin/pip install -q -r requirements.txt

echo "--- Creating systemd service ---"
cat > /etc/systemd/system/$APP.service << 'SERVICE'
[Unit]
Description=$APP
After=network.target

[Service]
WorkingDirectory=/app/$APP
ExecStart=/app/$APP/.venv/bin/uvicorn main:app --host 127.0.0.1 --port $PORT
Restart=always
User=root

[Install]
WantedBy=multi-user.target
SERVICE

systemctl daemon-reload
systemctl enable $APP
systemctl start $APP

echo "--- Configuring nginx ---"
cat > /etc/nginx/sites-available/$APP << 'NGINX'
server {
    listen 80;
    server_name _;

    location / {
        proxy_pass http://127.0.0.1:$PORT;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
    }
}
NGINX

ln -sf /etc/nginx/sites-available/$APP /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl reload nginx

echo "==> Done. $APP is running on port 80."
EOF
