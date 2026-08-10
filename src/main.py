"""
main.py
-------
OBS script lifecycle entry point.

This is the file that OBS loads via Tools → Scripts.  It wires together
all the modules:

1. ConfigManager  - persistent JSON DB
2. EventHandler   - scene-change callback
3. HTTP Server    - embedded web server for the browser dock UI

It also exposes the standard OBS script_*() hooks and a minimal
script_properties() panel so the user can see the dock URL without
opening the script log.
"""

import os
import traceback

import obspython as obs

from .constants import PLUGIN_LOG_PREFIX, PLUGIN_VERSION, DEFAULT_HTTP_PORT
from .config_manager import ConfigManager
from .event_handler import event_handler_init, event_handler_shutdown
from .http_server import http_server_start, http_server_stop
from .obs_helpers import current_scene_name
from .audio_engine import apply_rules_for_scene


# ==========================================================================
# Module-level state
# ==========================================================================
_config = None    # type: ConfigManager | None


# ==========================================================================
# OBS lifecycle hooks
# ==========================================================================

def script_description():
    return (
        "Per-Scene Audio Control  v%s\n\n"
        "Automatically mutes / unmutes and sets volume levels for your\n"
        "audio tracks based on the active scene.  Configure everything\n"
        "from the dockable browser panel.\n\n"
        "After loading this script, add a Custom Browser Dock:\n"
        "  Docks → Custom Browser Docks → http://127.0.0.1:%d\n"
    ) % (PLUGIN_VERSION, DEFAULT_HTTP_PORT)


def script_load(settings):
    """Called once when the script is loaded or OBS starts."""
    global _config
    try:
        obs.script_log(obs.LOG_INFO, "%s Loading v%s ..." % (PLUGIN_LOG_PREFIX, PLUGIN_VERSION))

        # 1. Initialise the config manager (JSON DB next to this script)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        _config = ConfigManager(db_dir=script_dir)
        _config.load()

        # 2. Register the scene-change event handler
        event_handler_init(_config)

        # 3. Start the embedded HTTP server
        http_server_start(_config)

        # 4. Apply rules for the current scene immediately
        scene = current_scene_name()
        if scene:
            apply_rules_for_scene(scene, _config.get_rules())

        obs.script_log(obs.LOG_INFO, "%s Loaded successfully." % PLUGIN_LOG_PREFIX)
    except Exception:
        obs.script_log(
            obs.LOG_ERROR,
            "%s script_load crashed:\n%s" % (PLUGIN_LOG_PREFIX, traceback.format_exc()),
        )


def script_unload():
    """Called when the script is removed or OBS shuts down."""
    try:
        event_handler_shutdown()
        http_server_stop()
        obs.script_log(obs.LOG_INFO, "%s Unloaded." % PLUGIN_LOG_PREFIX)
    except Exception:
        obs.script_log(
            obs.LOG_ERROR,
            "%s script_unload crashed:\n%s" % (PLUGIN_LOG_PREFIX, traceback.format_exc()),
        )


def script_save(settings):
    """Called when OBS saves the scene collection - persist our config."""
    if _config:
        _config.save()


def script_properties():
    """
    Minimal properties panel shown in Tools → Scripts.
    Just shows the dock URL so the user knows where to point their browser dock.
    """
    props = obs.obs_properties_create()

    port = DEFAULT_HTTP_PORT
    if _config:
        port = _config.get_settings().get("http_port", DEFAULT_HTTP_PORT)

    p = obs.obs_properties_add_text(
        props, "dock_url_display",
        "Dock URL (add as Custom Browser Dock)",
        obs.OBS_TEXT_DEFAULT,
    )
    obs.obs_property_set_enabled(p, False)

    # Pre-fill the display text via a data object
    data = obs.obs_data_create()
    obs.obs_data_set_string(data, "dock_url_display", "http://127.0.0.1:%d" % port)
    obs.obs_properties_apply_settings(props, data)
    obs.obs_data_release(data)

    return props
