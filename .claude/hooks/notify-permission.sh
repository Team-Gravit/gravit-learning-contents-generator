#!/bin/bash
# Notification hook: 권한 승인 / 질문 알림

MSG="권한 승인이 필요합니다."
TITLE="Claude Code"

OS=$(uname -s)
if [ "$OS" = "Darwin" ]; then
  osascript -e "display notification \"$MSG\" with title \"$TITLE\"" 2>/dev/null
elif grep -qi microsoft /proc/version 2>/dev/null; then
  powershell.exe -Command "[void](New-BurntToastNotification -Text '$TITLE','$MSG')" 2>/dev/null \
    || powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; [System.Windows.Forms.MessageBox]::Show('$MSG','$TITLE')" 2>/dev/null
else
  notify-send "$TITLE" "$MSG" 2>/dev/null
fi

exit 0