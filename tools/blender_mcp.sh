#!/usr/bin/env bash
# Headless Blender + MCP for Blender.
#   tools/blender_mcp.sh start    start Blender (no GUI) with the addon server on localhost:9876
#   tools/blender_mcp.sh status   is it listening?
#   tools/blender_mcp.sh stop
#   tools/blender_mcp.sh install  (re)install Blender 4.5 LTS + the addon (fresh container)
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
LOG=/tmp/blender-mcp.log
PIDF=/tmp/blender-mcp.pid
BV=4.5.16
case "${1:-status}" in
  install)
    if ! command -v blender >/dev/null; then
      cd /opt
      curl -sSLO "https://download.blender.org/release/Blender4.5/blender-$BV-linux-x64.tar.xz"
      curl -sSL "https://download.blender.org/release/Blender4.5/blender-$BV.sha256" | grep linux-x64 | sha256sum -c -
      tar -xf "blender-$BV-linux-x64.tar.xz" && rm "blender-$BV-linux-x64.tar.xz"
      ln -sf "/opt/blender-$BV-linux-x64/blender" /usr/local/bin/blender
    fi
    D="$HOME/.config/blender/4.5/scripts/addons"; mkdir -p "$D"
    DISABLE_TELEMETRY=true BLENDERMCP_ADDONS_DIR="$D" uvx mcp-for-blender install-addon
    ;;
  start)
    if [[ -f $PIDF ]] && kill -0 "$(cat $PIDF)" 2>/dev/null; then echo "already running (pid $(cat $PIDF))"; exit 0; fi
    DISABLE_TELEMETRY=true nohup blender -b --factory-startup -noaudio --python "$ROOT/tools/blender_mcp_headless.py" > "$LOG" 2>&1 &
    echo $! > $PIDF
    for _ in $(seq 1 60); do grep -q "listening on" "$LOG" 2>/dev/null && break; sleep 0.5; done
    grep "listening on" "$LOG" || { echo "failed to start; see $LOG"; tail -20 "$LOG"; exit 1; }
    ;;
  status)
    if [[ -f $PIDF ]] && kill -0 "$(cat $PIDF)" 2>/dev/null; then echo "running (pid $(cat $PIDF)) on localhost:9876"; else echo "not running"; fi
    ;;
  stop)
    [[ -f $PIDF ]] && kill "$(cat $PIDF)" 2>/dev/null || true; rm -f $PIDF; echo stopped
    ;;
esac
