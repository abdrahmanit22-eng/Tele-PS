#!/data/data/com.termux/files/usr/bin/bash
# ============================================================
#   Tele-Ps - one-click setup for Android Termux
#   Made by Abdelrahman
#   Usage: bash setup_termux.sh
# ============================================================
set -e
cd "$(dirname "$0")"

echo "[*] Tele-Ps setup for Termux - Made by Abdelrahman"
echo "[*] Updating packages ..."
pkg update -y
pkg install -y python

echo "[*] Installing Python dependencies ..."
pip install -r requirements.txt

echo "[*] Starting Tele-Ps web tool ..."
nohup python server.py --host 0.0.0.0 --port 8080 > /tmp/teleps_web.log 2>&1 &
sleep 2

echo "[+] Tele-Ps WEB is running!"
echo "    On this phone : http://127.0.0.1:8080"
IP=$(python -c "import socket;s=socket.socket(socket.AF_INET,socket.SOCK_DGRAM);s.connect(('8.8.8.8',80));print(s.getsockname()[0])" 2>/dev/null || true)
[ -n "$IP" ] && echo "    From your LAN : http://$IP:8080"
echo ""
echo "[+] Optional Termux add-ons:"
echo "    pkg install termux-api   -> screenshots (/shot work)"
echo "    pkg install termux-boot  -> auto-start persistence (/persist at boot)"
echo ""
echo "[+] Tip: keep a session alive with:  termux-wake-lock"
echo "    (Made by Abdelrahman)"
