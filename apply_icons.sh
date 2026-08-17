#!/bin/bash
# Tele-Ps icon installer: hicolor icons, desktop launcher, mimetype
set -e
ROOT="$(cd "$(dirname "$0")" && pwd)"
ICONS="$ROOT/icons"
HICOLOR="$HOME/.local/share/icons/hicolor"
APPS="$HOME/.local/share/applications"
MIME="$HOME/.local/share/mime/packages"

echo "[*] Installing Tele-Ps icons ..."
mkdir -p "$HICOLOR/512x512/apps" "$HICOLOR/256x256/apps" "$HICOLOR/64x64/apps"
mkdir -p "$HICOLOR/48x48/apps" "$HICOLOR/32x32/apps" "$HICOLOR/16x16/apps"
mkdir -p "$APPS" "$MIME"

cp "$ICONS/tele-ps-512.png" "$HICOLOR/512x512/apps/tele-ps.png"
cp "$ICONS/tele-ps-256.png" "$HICOLOR/256x256/apps/tele-ps.png"
cp "$ICONS/tele-ps-64.png"  "$HICOLOR/64x64/apps/tele-ps.png"
# downscale leftovers if convert/python available
python3 - << PY
from PIL import Image
src = "$ICONS/tele-ps-512.png"
for s in (48, 32, 16):
    Image.open(src).resize((s, s), Image.LANCZOS).save("$HICOLOR/%dx%d/apps/tele-ps.png" % (s, s))
print("[+] extra hicolor sizes 48/32/16")
PY

cat > "$APPS/tele-ps.desktop" << EOF
[Desktop Entry]
Type=Application
Name=Tele-Ps
GenericName=Telegram C2 Agent Builder
Comment=Tele-Ps Telegram-C2 agent builder - Made by Abdelrahman
Exec=python3 $ROOT/server.py
Icon=tele-ps
Terminal=true
Categories=Development;Security;
StartupNotify=true
MimeType=text/x-teleps-agent;
EOF

cat > "$MIME/tele-ps.xml" << 'EOF'
<?xml version="1.0" encoding="UTF-8"?>
<mime-info xmlns="http://www.freedesktop.org/standards/shared-mime-info">
  <mime-type type="text/x-teleps-agent">
    <comment>Tele-Ps agent</comment>
    <glob pattern="teleps_agent*.py"/>
    <icon name="tele-ps"/>
  </mime-type>
</mime-info>
EOF

if command -v update-desktop-database >/dev/null 2>&1; then
    update-desktop-database "$APPS" 2>/dev/null || true
fi
if command -v update-mime-database >/dev/null 2>&1; then
    update-mime-database "$HOME/.local/share/mime" 2>/dev/null || true
fi
if command -v gtk-update-icon-cache >/dev/null 2>&1; then
    gtk-update-icon-cache -f -t "$HICOLOR" 2>/dev/null || true
fi

chmod +x "$APPS/tele-ps.desktop"
echo "[+] Desktop launcher: $APPS/tele-ps.desktop"
echo "[+] Icons installed under $HICOLOR"
echo "[+] Mimetype: text/x-teleps-agent for teleps_agent*.py"
echo "[+] Done. Tele-Ps - Made by Abdelrahman"
