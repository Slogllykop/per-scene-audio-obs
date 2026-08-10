"""
http_server.py
--------------
Embeds a lightweight HTTP server inside the OBS process.

Runs in a daemon thread so it never blocks the OBS UI.  The server
injects references to the config_manager and OBS helper functions into
the HTTPServer instance so the ApiHandler can reach them without globals.
"""

import threading
import socketserver
from http.server import HTTPServer

import obspython as obs

from .constants import PLUGIN_LOG_PREFIX, HTTP_HOST, DEFAULT_HTTP_PORT
from .obs_helpers import get_scene_names, get_audio_track_names, current_scene_name
from .audio_engine import apply_rules_for_scene
from .ui.templates import get_dock_html
from .ui.api_routes import ApiHandler


class _ReusableTCPServer(HTTPServer):
    """HTTPServer subclass that allows immediate port reuse on restart."""
    allow_reuse_address = True
    # Shorten the timeout so shutdown() isn't sluggish
    timeout = 1


# Module-level state
_server = None        # type: _ReusableTCPServer | None
_thread = None        # type: threading.Thread | None
_config_manager = None


def http_server_start(config_manager, port=None):
    """
    Start the embedded HTTP server in a daemon thread.

    Parameters
    ----------
    config_manager : ConfigManager
    port : int or None
        Override the port (otherwise uses config_manager's setting or default).
    """
    global _server, _thread, _config_manager
    _config_manager = config_manager

    if port is None:
        port = config_manager.get_settings().get("http_port", DEFAULT_HTTP_PORT)

    # Build the dock HTML with the correct port baked in
    dock_html = get_dock_html(port)

    _server = _ReusableTCPServer((HTTP_HOST, port), ApiHandler)
    # Inject dependencies so the handler can access them via self.server
    _server.config_manager = config_manager
    _server.dock_html = dock_html
    _server.get_obs_state = _get_obs_state
    _server.apply_callback = _apply_current_scene

    _thread = threading.Thread(target=_server.serve_forever, daemon=True)
    _thread.start()

    obs.script_log(
        obs.LOG_INFO,
        "%s HTTP server started on http://%s:%d" % (PLUGIN_LOG_PREFIX, HTTP_HOST, port),
    )
    obs.script_log(
        obs.LOG_INFO,
        "%s → Add a Custom Browser Dock in OBS pointing to http://%s:%d" % (PLUGIN_LOG_PREFIX, HTTP_HOST, port),
    )


def http_server_stop():
    """Shut down the HTTP server gracefully."""
    global _server, _thread
    if _server:
        _server.shutdown()
        obs.script_log(obs.LOG_INFO, "%s HTTP server stopped." % PLUGIN_LOG_PREFIX)
    _server = None
    _thread = None


# ------------------------------------------------------------------
# Callbacks injected into the server
# ------------------------------------------------------------------

def _get_obs_state():
    """Return (scenes, audio_tracks, current_scene)."""
    return (
        get_scene_names(),
        get_audio_track_names(),
        current_scene_name(),
    )


def _apply_current_scene():
    """Apply rules for whatever scene is currently on program."""
    if _config_manager is None:
        return
    scene = current_scene_name()
    if scene:
        apply_rules_for_scene(scene, _config_manager.get_rules())
