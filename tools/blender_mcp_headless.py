"""Run the MCP for Blender addon's socket server inside a headless Blender (no GUI, no X display).

The addon refuses to start in `blender -b` because it relies on bpy.app.timers to run commands on the main
thread, and timers never fire in background mode. This runner starts the same server and drives its command
queue from the main thread itself, so the MCP server (`uvx mcp-for-blender`) can talk to it on localhost:9876.

usage:  blender -b --python tools/blender_mcp_headless.py                (or tools/blender_mcp.sh start)
Security: the socket has no authentication and runs arbitrary Python; it is bound to localhost only.
"""
import socket
import sys
import threading
import time

import addon_utils
import bpy

addon_utils.enable("blender_mcp", default_set=True, persistent=True)
import blender_mcp as addon  # noqa: E402  (the module only exists once the addon is enabled)

HOST, PORT = "localhost", 9876
srv = addon.BlenderMCPServer(host=HOST, port=PORT)
srv.running = True
srv.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
srv.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
srv.socket.bind((HOST, PORT))
srv.socket.listen(5)
srv.server_thread = threading.Thread(target=srv._server_loop, daemon=True)
srv.server_thread.start()
try:
    bpy.context.scene.blendermcp_server_running = True
except Exception:
    pass
print(f"BlenderMCP headless server listening on {HOST}:{PORT} (Blender {bpy.app.version_string})", flush=True)

try:
    while srv.running:
        srv._drain_command_queue()      # runs queued commands on this (main) thread
        time.sleep(0.02)
except KeyboardInterrupt:
    pass
finally:
    srv.running = False
    srv.socket.close()
    sys.exit(0)
