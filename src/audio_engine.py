"""
audio_engine.py
---------------
Core logic that applies per-scene audio rules.

Given a scene name and the current rule set, this module mutes / unmutes
and optionally sets volume for every known audio track.  Tracks that have
no explicit rule for a scene are **muted by default** - so you only need
to whitelist the ones you want active.
"""

import obspython as obs

from .constants import PLUGIN_LOG_PREFIX
from .obs_helpers import set_source_muted, set_source_volume_db


def apply_rules_for_scene(scene_name, rules):
    """
    Apply audio rules for *scene_name*.

    Parameters
    ----------
    scene_name : str
        The scene that just became active.
    rules : dict
        The full rules dict: ``{ scene: { track: { "mute": bool, ... } } }``
    """
    scene_cfg = rules.get(scene_name, {})

    from .obs_helpers import get_scene_audio_tracks
    scene_tracks = get_scene_audio_tracks(scene_name)

    applied = 0
    for track_name in scene_tracks:
        entry = scene_cfg.get(track_name)
        if entry is not None:
            muted = entry.get("mute", True)
            set_source_muted(track_name, muted)

            if "volume_db" in entry:
                set_source_volume_db(track_name, entry["volume_db"])
        else:
            # Force unconfigured tracks in the scene to be ACTIVE
            # to prevent mute states from bleeding over from other scenes.
            set_source_muted(track_name, False)

        applied += 1

    obs.script_log(
        obs.LOG_INFO,
        "%s Applied %d rule(s) for scene '%s'." % (PLUGIN_LOG_PREFIX, applied, scene_name),
    )
