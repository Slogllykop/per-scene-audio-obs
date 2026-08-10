"""
obs_helpers.py
--------------
Thin wrappers around obspython calls.

Keeps the rest of the codebase free from raw OBS API boilerplate
(especially the get→use→release pattern for sources).
"""

import obspython as obs


def get_scene_names():
    """Return a sorted list of all scene names in the current collection."""
    names = []
    scenes = obs.obs_frontend_get_scenes()
    if scenes:
        for s in scenes:
            names.append(obs.obs_source_get_name(s))
        obs.source_list_release(scenes)
    return sorted(names)


def get_audio_track_names():
    """Return a sorted list of every source that has an audio output."""
    names = []
    sources = obs.obs_enum_sources()
    if sources:
        for s in sources:
            flags = obs.obs_source_get_output_flags(s)
            if flags & obs.OBS_SOURCE_AUDIO:
                names.append(obs.obs_source_get_name(s))
        obs.source_list_release(sources)
    return sorted(names)


def current_scene_name():
    """Return the name of the active program scene, or None."""
    src = obs.obs_frontend_get_current_scene()
    if src is None:
        return None
    name = obs.obs_source_get_name(src)
    obs.obs_source_release(src)
    return name


def set_source_muted(track_name, muted):
    """Mute or unmute a source by name.  Returns True on success."""
    source = obs.obs_get_source_by_name(track_name)
    if source is None:
        return False
    obs.obs_source_set_muted(source, muted)
    obs.obs_source_release(source)
    return True


def set_source_volume_db(track_name, volume_db):
    """
    Set a source's volume in dB.  Converts from dB to the linear
    multiplier that OBS expects internally.
    """
    source = obs.obs_get_source_by_name(track_name)
    if source is None:
        return False
    linear = 10 ** (volume_db / 20.0)
    obs.obs_source_set_volume(source, linear)
    obs.obs_source_release(source)
    return True


def get_source_muted(track_name):
    """Return whether a source is currently muted, or None if not found."""
    source = obs.obs_get_source_by_name(track_name)
    if source is None:
        return None
    muted = obs.obs_source_get_muted(source)
    obs.obs_source_release(source)
    return muted


def get_source_volume_db(track_name):
    """Return a source's volume in dB, or None if not found."""
    source = obs.obs_get_source_by_name(track_name)
    if source is None:
        return None
    import math
    linear = obs.obs_source_get_volume(source)
    obs.obs_source_release(source)
    if linear <= 0:
        return -96.0  # effectively silent
    return 20.0 * math.log10(linear)
