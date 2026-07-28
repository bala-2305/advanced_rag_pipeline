"""Incremental file tracking engine for mzero."""

import os
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Tuple
from mzero.utils.logger import logger


class IncrementalTracker:
    def __init__(self, state_file_path: str = ".mzero/state.json"):
        self.state_file_path = state_file_path
        self.file_states: Dict[str, Dict[str, str]] = {}
        self.load_state()

    def load_state(self) -> None:
        if os.path.exists(self.state_file_path):
            try:
                with open(self.state_file_path, "r", encoding="utf-8") as f:
                    self.file_states = json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load incremental state: {e}. Rebuilding state.")
                self.file_states = {}
        else:
            self.file_states = {}

    def save_state(self) -> None:
        os.makedirs(os.path.dirname(self.state_file_path), exist_ok=True)
        try:
            with open(self.state_file_path, "w", encoding="utf-8") as f:
                json.dump(self.file_states, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save incremental state: {e}")

    @staticmethod
    def compute_file_hash(file_path: str) -> str:
        hasher = hashlib.sha256()
        try:
            with open(file_path, "rb") as f:
                while chunk := f.read(65536):
                    hasher.update(chunk)
            return hasher.hexdigest()
        except Exception as e:
            logger.error(f"Error computing hash for {file_path}: {e}")
            return ""

    def scan_directory(self, dir_path: str) -> Tuple[List[str], List[str], List[str]]:
        """Returns (added_files, modified_files, deleted_files)."""
        current_files: Set[str] = set()
        added_files: List[str] = []
        modified_files: List[str] = []

        if not os.path.exists(dir_path):
            return added_files, modified_files, []

        p = Path(dir_path)
        if p.is_file():
            all_paths = [p]
        else:
            all_paths = [f for f in p.rglob("*") if f.is_file() and not f.name.startswith(".")]

        for file_path in all_paths:
            abs_path = str(file_path.resolve())
            current_files.add(abs_path)
            file_hash = self.compute_file_hash(abs_path)
            
            if abs_path not in self.file_states:
                added_files.append(abs_path)
                self.file_states[abs_path] = {"hash": file_hash, "path": abs_path}
            elif self.file_states[abs_path].get("hash") != file_hash:
                modified_files.append(abs_path)
                self.file_states[abs_path] = {"hash": file_hash, "path": abs_path}

        # Check for deleted files
        stored_paths = set(self.file_states.keys())
        deleted_files = list(stored_paths - current_files)
        for deleted in deleted_files:
            del self.file_states[deleted]

        self.save_state()
        return added_files, modified_files, deleted_files
