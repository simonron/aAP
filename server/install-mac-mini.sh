#!/bin/zsh
set -e
APP="$HOME/Library/Application Support/aAP"
PLIST="$HOME/Library/LaunchAgents/uk.co.aap.shared-server.plist"
mkdir -p "$APP" "$HOME/Library/LaunchAgents"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cp "$SCRIPT_DIR/aap_server.py" "$APP/aap_server.py"
cat > "$PLIST" <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
<key>Label</key><string>uk.co.aap.shared-server</string>
<key>ProgramArguments</key><array><string>/usr/bin/python3</string><string>$APP/aap_server.py</string></array>
<key>RunAtLoad</key><true/><key>KeepAlive</key><true/>
<key>StandardOutPath</key><string>$APP/server.log</string>
<key>StandardErrorPath</key><string>$APP/server-error.log</string>
</dict></plist>
EOF
launchctl bootout gui/$(id -u) "$PLIST" 2>/dev/null || true
launchctl bootstrap gui/$(id -u) "$PLIST"
launchctl kickstart -k gui/$(id -u)/uk.co.aap.shared-server
echo "aAP server installed and running on port 8788"
echo "Data: $APP/records.json"
echo "Log:  $APP/server.log"
