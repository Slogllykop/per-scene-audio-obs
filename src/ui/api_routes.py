"""
api_routes.py
-------------
HTTP request handler for the embedded server.

Translates browser-dock fetch() calls into config_manager / obs_helpers
operations.  All endpoints return JSON.

Routes
------
GET  /                    → serves the dock HTML page
GET  /api/state           → { scenes, current_scene }
GET  /api/rules           → { rules: { ... } }
GET  /api/scene_tracks?scene=X → { tracks: [ {name, mute, volume_db}, ... ] }
POST /api/rule            → upsert one rule   { scene, track, active, volume_db? }
POST /api/remove_rule     → delete one rule    { scene, track }
POST /api/apply           → re-apply rules for the current scene
POST /api/clear_scene     → delete all rules for a scene  { scene }
POST /api/clear_all       → wipe every rule
"""

import json
import traceback
from http.server import BaseHTTPRequestHandler
import obspython as obs

from ..constants import PLUGIN_LOG_PREFIX


def _api_log(msg):
    obs.script_log(obs.LOG_DEBUG, "%s [HTTP] %s" % (PLUGIN_LOG_PREFIX, msg))


class ApiHandler(BaseHTTPRequestHandler):
    """
    Thin HTTP handler.  ``self.server`` must have these attributes
    injected by http_server.py:

    * ``config_manager``        - a ConfigManager instance
    * ``get_obs_state``         - callable returning (scenes, current_scene)
    * ``get_scene_tracks_cb``   - callable(scene_name) returning [{name, mute, volume_db}, ...]
    * ``apply_callback``        - callable that applies rules for the current scene
    * ``dock_html``             - the rendered HTML string to serve at /
    """

    # Silence default stderr logging to prevent spam
    def log_message(self, fmt, *args):
        pass

    # ------------------------------------------------------------------
    # CORS headers (browser dock runs on a different origin)
    # ------------------------------------------------------------------

    def _cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        """Handle CORS preflight."""
        self.send_response(200)
        self._cors_headers()
        self.end_headers()

    # ------------------------------------------------------------------
    # GET routes
    # ------------------------------------------------------------------

    def do_GET(self):
        try:
            if self.path == "/" or self.path == "/index.html":
                self._serve_html()
            elif self.path == "/api/state":
                self._get_state()
            elif self.path == "/api/rules":
                self._get_rules()
            elif self.path.startswith("/api/scene_tracks"):
                self._get_scene_tracks()
            else:
                self._not_found()
        except Exception:
            self._error(traceback.format_exc())

    def _serve_html(self):
        html = getattr(self.server, "dock_html", "<h1>Per-Scene Audio</h1>")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(html.encode("utf-8"))

    def _get_state(self):
        getter = getattr(self.server, "get_obs_state", None)
        if getter:
            scenes, current = getter()
        else:
            scenes, current = [], None
        self._json_response({
            "scenes": scenes,
            "current_scene": current,
        })

    def _get_rules(self):
        cm = getattr(self.server, "config_manager", None)
        rules = cm.get_rules() if cm else {}
        self._json_response({"rules": rules})

    def _get_scene_tracks(self):
        """
        GET /api/scene_tracks?scene=SceneName

        Returns the audio tracks belonging to a specific scene (including
        nested scenes).  Each track includes its current OBS mixer state
        so the UI can show defaults.
        """
        # Parse query string for ?scene=
        scene_name = ""
        if "?" in self.path:
            query = self.path.split("?", 1)[1]
            for param in query.split("&"):
                if param.startswith("scene="):
                    # URL-decode the scene name
                    from urllib.parse import unquote
                    scene_name = unquote(param[6:])
                    break

        if not scene_name:
            self._json_response({"error": "scene parameter required"}, 400)
            return

        getter = getattr(self.server, "get_scene_tracks_cb", None)
        if getter:
            tracks = getter(scene_name)
        else:
            tracks = []

        self._json_response({"scene": scene_name, "tracks": tracks})

    # ------------------------------------------------------------------
    # POST routes
    # ------------------------------------------------------------------

    def do_POST(self):
        try:
            if self.path == "/api/rule":
                self._post_rule()
            elif self.path == "/api/remove_rule":
                self._post_remove_rule()
            elif self.path == "/api/apply":
                self._post_apply()
            elif self.path == "/api/clear_scene":
                self._post_clear_scene()
            elif self.path == "/api/clear_all":
                self._post_clear_all()
            else:
                self._not_found()
        except Exception:
            self._error(traceback.format_exc())

    def _post_rule(self):
        body = self._read_json()
        scene = body.get("scene", "")
        track = body.get("track", "")
        active = body.get("active", False)
        volume_db = body.get("volume_db", None)

        if not scene or not track:
            self._json_response({"error": "scene and track required"}, 400)
            return

        entry = {"mute": not active}
        if volume_db is not None:
            entry["volume_db"] = float(volume_db)

        cm = getattr(self.server, "config_manager", None)
        if cm:
            cm.set_rule(scene, track, entry)
            _api_log("Rule set: %s / %s -> %s" % (scene, track, entry))

        # Auto-apply if this scene is currently live
        self._auto_apply_if_live(scene)
        self._json_response({"ok": True})

    def _post_remove_rule(self):
        body = self._read_json()
        scene = body.get("scene", "")
        track = body.get("track", "")
        cm = getattr(self.server, "config_manager", None)
        if cm:
            cm.remove_rule(scene, track)
        self._auto_apply_if_live(scene)
        self._json_response({"ok": True})

    def _post_apply(self):
        cb = getattr(self.server, "apply_callback", None)
        if cb:
            cb()
        self._json_response({"ok": True})

    def _post_clear_scene(self):
        body = self._read_json()
        scene = body.get("scene", "")
        cm = getattr(self.server, "config_manager", None)
        if cm and scene:
            rules = cm.get_rules()
            if scene in rules:
                for track in list(rules[scene].keys()):
                    cm.remove_rule(scene, track)
        self._json_response({"ok": True})

    def _post_clear_all(self):
        cm = getattr(self.server, "config_manager", None)
        if cm:
            cm.clear_rules()
        self._json_response({"ok": True})

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    def _auto_apply_if_live(self, scene):
        """If the edited scene is the one currently on program, re-apply."""
        getter = getattr(self.server, "get_obs_state", None)
        cb = getattr(self.server, "apply_callback", None)
        if getter and cb:
            _, current = getter()
            if current == scene:
                cb()

    def _read_json(self):
        length = int(self.headers.get("Content-Length", 0))
        if length == 0:
            return {}
        raw = self.rfile.read(length)
        return json.loads(raw.decode("utf-8"))

    def _json_response(self, data, code=200):
        body = json.dumps(data).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self._cors_headers()
        self.end_headers()
        self.wfile.write(body)

    def _not_found(self):
        self._json_response({"error": "not found"}, 404)

    def _error(self, detail):
        _api_log("HTTP handler error: " + detail)
        self._json_response({"error": "internal error", "traceback": detail}, 500)
