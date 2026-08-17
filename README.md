# Tele-Ps - Telegram-C2 Agent Builder (Web)
Tool Made by Abdelrahman

A Python RAT builder with a **web interface**. It uses **only a Telegram bot**
as the command & control channel. **No IP address, no domain, no VPS required** -
you control the agent by sending messages to your bot from Telegram.

Works on: **Windows / Linux / macOS / Android (Termux)** - both the builder and
the generated agent.

## Contents
- `server.py` - the web app (Flask). THIS is the main entry point.
- `builder.py` - shared build engine (used by both web + CLI)
- `template.py` - the agent source template
- `setup_termux.sh` - one-click installer for Android Termux
- `requirements.txt` - Python dependencies
- `builds/` - generated agents are saved here

## Run the web tool (desktop)
```
pip install -r requirements.txt
python3 server.py
```
Open **http://127.0.0.1:8080** in your browser.

Want to reach it from other devices on your network?
```
python3 server.py --host 0.0.0.0
```
It will print your LAN address, e.g. http://192.168.1.5:8080

## Run the web tool (Android Termux)
```
pkg update -y
pkg install -y python
pip install -r requirements.txt
bash setup_termux.sh
```
Open **http://127.0.0.1:8080** in your phone's browser.
The setup script also installs everything and starts the server for you.

Optional Termux add-ons:
- `pkg install termux-api` -> screenshots (/shot) work on Android
- `pkg install termux-boot` -> /persist can auto-start the agent at boot
- `termux-wake-lock` keeps the phone session alive

## Web UI features
1. Paste your **Telegram bot token** (from @BotFather).
2. Paste your **chat ID**.
3. Pick build mode: **Plain** or **Obfuscated** (hides the token).
4. Optional: test the credentials with Telegram first (sends you a test message).
5. Click **BUILD AGENT** -> the generated `.py` file downloads instantly.

## Agent commands (via Telegram chat)
- `/help` or `/start` - show help
- `/sysinfo` - host, user, OS, public IP (+ device model & Android version on Termux)
- `/shot` - screenshot (mss on desktop, termux-api on Android)
- `/download <path>` - pull a file from the target
- `/persist` - install autostart persistence
  - Windows: HKCU Run key
  - Linux: ~/.config/autostart
  - macOS: LaunchAgent
  - Termux: ~/.termux/boot + ~/.bashrc hook
- `/kill` - stop the agent
- any other text - executed as a shell command on the target
- sending a document to the bot uploads it to the target

## Getting bot token + chat ID
1. Talk to `@BotFather` on Telegram, `/newbot`, copy the token.
2. Chat ID: message `@userinfobot`, or send your bot a message then check
   `https://api.telegram.org/bot<TOKEN>/getUpdates`.

## Notes
- For education/authorized testing only.
- Keep the bot token private; anyone with it controls the agent.
