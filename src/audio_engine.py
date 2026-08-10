"""
audio_engine.py
---------------
Core logic that applies per-scene audio rules.

Given a scene name and the current rule set, this module mutes / unmutes
and optionally sets volume for every known audio track.  Tracks that have
no explicit rule for a scene are **muted by default** — so you only need
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
    scene_cfg = rules.get(scene_name)
    if scene_cfg is None:
        obs.script_log(
            obs.LOG_INFO,
            "%s No rules for scene '%s' — audio left untouched." % (PLUGIN_LOG_PREFIX, scene_name),
        )
        return

    # Collect every track mentioned in *any* scene so we can mute the
    # ones that aren't explicitly listed for the current scene.
    all_tracks = _all_known_tracks(rules)

    applied = 0
    for track_name in all_tracks:
        entry = scene_cfg.get(track_name, {"mute": True})

        muted = entry.get("mute", True)
        set_source_muted(track_name, muted)

        if "volume_db" in entry:
            set_source_volume_db(track_name, entry["volume_db"])

        applied += 1

    obs.script_log(
        obs.LOG_INFO,
        "%s Applied %d rule(s) for scene '%s'." % (PLUGIN_LOG_PREFIX, applied, scene_name),
    )


def _all_known_tracks(rules):
    """Return the set of every track name referenced across all scenes."""
    tracks = set()
    for cfg in rules.values():
        tracks.update(cfg.keys())
    return tracks
