"""
obs_helpers.py
--------------
Thin wrappers around obspython calls.

Keeps the rest of the codebase free from raw OBS API boilerplate
(especially the get→use→release pattern for sources).
"""

import math
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


def get_scene_audio_tracks(scene_name):
    """
    Return a sorted list of audio source names that belong to a specific
    scene, including sources inside nested scenes (recursively).
    """
    result = set()
    visited_scenes = set()  # prevent infinite loops from circular nesting
    try:
        _collect_audio_from_scene(scene_name, result, visited_scenes)
    except Exception as e:
        import traceback
        err_msg = f"[PerSceneAudio] Crash in get_scene_audio_tracks: {e}\n{traceback.format_exc()}"
        obs.script_log(obs.LOG_WARNING, err_msg)
    return sorted(result)


def _collect_audio_from_scene(scene_name, result, visited_scenes):
    """Recursively collect audio sources from a scene and its nested scenes."""
    if scene_name in visited_scenes:
        return
    visited_scenes.add(scene_name)

    # Get the source for this scene by name
    scene_source = obs.obs_get_source_by_name(scene_name)
    if scene_source is None:
        return

    # Get the scene object from the source
    scene_obj = obs.obs_scene_from_source(scene_source)
    obs.obs_source_release(scene_source)
    if scene_obj is None:
        return

    # Enumerate all items in this scene
    items = obs.obs_scene_enum_items(scene_obj)
    if items is None:
        return

    for item in items:
        item_source = obs.obs_sceneitem_get_source(item)
        if item_source is None:
            continue

        source_name = obs.obs_source_get_name(item_source)
        flags = obs.obs_source_get_output_flags(item_source)

        # Check if this source has audio output
        if flags & obs.OBS_SOURCE_AUDIO:
            result.add(source_name)

        # Check if this source is a scene (nested scene) - recurse
        # A scene source has the OBS_SOURCE_COMPOSITE flag or can be
        # converted via obs_scene_from_source
        nested_scene = obs.obs_scene_from_source(item_source)
        if nested_scene is not None:
            _collect_audio_from_scene(source_name, result, visited_scenes)
        else:
            # Also check for group sources which can contain items
            group_scene = obs.obs_group_from_source(item_source)
            if group_scene is not None:
                # Groups are scenes internally - recurse
                _collect_audio_from_scene(source_name, result, visited_scenes)

    obs.sceneitem_list_release(items)


def get_source_state(track_name):
    """
    Return the current mixer state of a source as a dict:
    {"mute": bool, "volume_db": float} or None if not found.
    """
    source = obs.obs_get_source_by_name(track_name)
    if source is None:
        return None
    muted = obs.obs_source_muted(source)
    linear = obs.obs_source_get_volume(source)
    obs.obs_source_release(source)
    if linear <= 0:
        vol_db = -96.0
    else:
        vol_db = 20.0 * math.log10(linear)
    return {"mute": muted, "volume_db": round(vol_db, 1)}


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
    muted = obs.obs_source_muted(source)
    obs.obs_source_release(source)
    return muted


def get_source_volume_db(track_name):
    """Return a source's volume in dB, or None if not found."""
    source = obs.obs_get_source_by_name(track_name)
    if source is None:
        return None
    linear = obs.obs_source_get_volume(source)
    obs.obs_source_release(source)
    if linear <= 0:
        return -96.0  # effectively silent
    return 20.0 * math.log10(linear)
