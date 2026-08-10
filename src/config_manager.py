"""
config_manager.py
-----------------
Manages the local JSON database that persists audio rules across OBS restarts.

The DB file lives next to the script (or in a user-configurable path).
All reads/writes go through this module so the rest of the codebase never
touches the filesystem directly.
"""

import json
import os
import copy
import traceback
import obspython as obs

from .constants import (
    DB_FILENAME,
    DEFAULT_DB,
    PLUGIN_LOG_PREFIX,
)


def _config_log(level, msg):
    """Unified logger — routes through OBS script log."""
    obs.script_log(level, "%s %s" % (PLUGIN_LOG_PREFIX, msg))


class ConfigManager:
    """
    Thread-safe-ish wrapper around a JSON file that stores per-scene
    audio rules and plugin settings.

    Public API
    ----------
    load()                           → read DB from disk (or create default)
    save()                           → flush current state to disk
    get_rules()                      → { scene: { track: entry } }
    set_rule(scene, track, entry)    → upsert one rule
    remove_rule(scene, track)        → delete one rule
    clear_rules()                    → wipe everything
    get_settings()                   → { ... }
    set_setting(key, value)          → update one setting
    """

    def __init__(self, db_dir=None):
        """
        Parameters
        ----------
        db_dir : str or None
            Directory where the JSON DB lives.  Defaults to the same
            directory as *this* source file (which, after build, is the
            directory of the single merged .py).
        """
        if db_dir is None:
            db_dir = os.path.dirname(os.path.abspath(__file__))
        self._db_path = os.path.join(db_dir, DB_FILENAME)
        self._data = copy.deepcopy(DEFAULT_DB)

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def load(self):
        """Load the JSON DB from disk.  Creates the default if missing."""
        if not os.path.exists(self._db_path):
            _config_log(obs.LOG_INFO,
                 "No DB found at %s — creating default." % self._db_path)
            self.save()
            return

        try:
            with open(self._db_path, "r", encoding="utf-8") as fh:
                raw = json.load(fh)
            # Merge with defaults so new keys are always present
            merged = copy.deepcopy(DEFAULT_DB)
            merged.update(raw)
            # Ensure nested dicts survive the shallow update
            if "rules" in raw:
                merged["rules"] = raw["rules"]
            if "settings" in raw:
                merged["settings"] = {**DEFAULT_DB["settings"], **raw["settings"]}
            self._data = merged
            _config_log(obs.LOG_INFO,
                 "Loaded DB from %s (%d scene(s))." % (self._db_path, len(self._data.get("rules", {}))))
        except Exception:
            _config_log(obs.LOG_ERROR,
                 "Failed to load DB — using defaults.\n" + traceback.format_exc())
            self._data = copy.deepcopy(DEFAULT_DB)

    def save(self):
        """Flush current state to the JSON file."""
        try:
            with open(self._db_path, "w", encoding="utf-8") as fh:
                json.dump(self._data, fh, indent=2, ensure_ascii=False)
        except Exception:
            _config_log(obs.LOG_ERROR,
                 "Failed to save DB.\n" + traceback.format_exc())

    # ------------------------------------------------------------------
    # Rules CRUD
    # ------------------------------------------------------------------

    def get_rules(self):
        """Return the full rules dict (reference, not copy)."""
        return self._data.get("rules", {})

    def set_rule(self, scene, track, entry):
        """
        Upsert a single rule.

        Parameters
        ----------
        scene : str
        track : str
        entry : dict   e.g. {"mute": False, "volume_db": -5.0}
        """
        rules = self._data.setdefault("rules", {})
        rules.setdefault(scene, {})[track] = entry
        self.save()

    def remove_rule(self, scene, track):
        """Remove a single rule.  No-op if it doesn't exist."""
        rules = self._data.get("rules", {})
        if scene in rules:
            rules[scene].pop(track, None)
            if not rules[scene]:
                del rules[scene]
            self.save()

    def clear_rules(self):
        """Wipe all rules."""
        self._data["rules"] = {}
        self.save()

    # ------------------------------------------------------------------
    # Settings helpers
    # ------------------------------------------------------------------

    def get_settings(self):
        return self._data.get("settings", {})

    def set_setting(self, key, value):
        self._data.setdefault("settings", {})[key] = value
        self.save()

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def get_db_path(self):
        return self._db_path
