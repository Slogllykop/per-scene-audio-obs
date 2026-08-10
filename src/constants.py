"""
constants.py
------------
Shared constants and defaults for the Per-Scene Audio plugin.
Centralizes magic strings, default ports, and configuration keys
so they can be changed in one place.
"""

# ==========================================================================
# Plugin metadata
# ==========================================================================
PLUGIN_NAME = "per_scene_audio"
PLUGIN_LOG_PREFIX = "[PerSceneAudio]"
PLUGIN_VERSION = "2.0.0"

# ==========================================================================
# Embedded HTTP server
# ==========================================================================
DEFAULT_HTTP_PORT = 18522          # Unlikely to collide with common services
HTTP_HOST = "127.0.0.1"           # Bind to localhost only - never expose

# ==========================================================================
# Local JSON DB
# ==========================================================================
DB_FILENAME = "per_scene_audio_db.json"

# Default DB structure - used when no file exists yet
DEFAULT_DB = {
    "version": 1,
    "rules": {},        # { scene_name: { track_name: { "mute": bool, "volume_db": float? } } }
    "settings": {
        "http_port": DEFAULT_HTTP_PORT,
    },
}

# ==========================================================================
# OBS event trigger
# ==========================================================================
# Which OBS frontend event triggers the audio override.
# "OBS_FRONTEND_EVENT_SCENE_CHANGED"        → fires immediately on switch
# "OBS_FRONTEND_EVENT_TRANSITION_STOP"      → fires after transition completes
TRIGGER_EVENT = "OBS_FRONTEND_EVENT_SCENE_CHANGED"
