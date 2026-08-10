"""
event_handler.py
----------------
Registers and handles OBS frontend events.

The only event we care about is the scene-change trigger (configurable
in constants.py).  When it fires, we pull the current scene name and
delegate to the audio engine.
"""

import traceback
import obspython as obs

from .constants import PLUGIN_LOG_PREFIX, TRIGGER_EVENT
from .obs_helpers import current_scene_name
from .audio_engine import apply_rules_for_scene


# Reference to the config manager — set by main.py during script_load
_config_manager = None


def event_handler_init(config_manager):
    """Store a reference to the config manager and register the OBS callback."""
    global _config_manager
    _config_manager = config_manager
    obs.obs_frontend_add_event_callback(_on_frontend_event)
    obs.script_log(obs.LOG_INFO, "%s Event handler registered." % PLUGIN_LOG_PREFIX)


def event_handler_shutdown():
    """Unregister the OBS callback."""
    obs.obs_frontend_remove_event_callback(_on_frontend_event)
    obs.script_log(obs.LOG_INFO, "%s Event handler unregistered." % PLUGIN_LOG_PREFIX)


def _on_frontend_event(event):
    """Called by OBS for every frontend event — we filter for scene changes."""
    try:
        if event == getattr(obs, TRIGGER_EVENT):
            scene = current_scene_name()
            if scene and _config_manager:
                apply_rules_for_scene(scene, _config_manager.get_rules())
    except Exception:
        obs.script_log(
            obs.LOG_ERROR,
            "%s Event handler crashed:\n%s" % (PLUGIN_LOG_PREFIX, traceback.format_exc()),
        )
