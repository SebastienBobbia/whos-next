"""
Team Manager — Gestion des membres de l'équipe avec persistance JSON.
"""

import json
import os
from pathlib import Path


class TeamManager:
    """Gère la liste des membres de l'équipe (ajout, suppression, persistance)."""

    def __init__(self, data_path: str | None = None):
        if data_path is None:
            # Stocke les données à côté de l'exécutable / du script
            app_dir = Path(__file__).parent
            self._data_dir = app_dir / "data"
        else:
            self._data_dir = Path(data_path)

        self._data_dir.mkdir(parents=True, exist_ok=True)
        self._file = self._data_dir / "team.json"
        self._members: list[str] = []
        self._load()

    # ── Public API ────────────────────────────────────────────

    @property
    def members(self) -> list[str]:
        """Retourne une copie de la liste des membres."""
        return list(self._members)

    def add_member(self, name: str) -> bool:
        """Ajoute un membre. Retourne False si le nom existe déjà."""
        clean = name.strip()
        if not clean:
            return False
        if clean in self._members:
            return False
        self._members.append(clean)
        self._save()
        return True

    def remove_member(self, name: str) -> bool:
        """Supprime un membre. Retourne False si introuvable."""
        try:
            self._members.remove(name)
            self._save()
            return True
        except ValueError:
            return False

    def rename_member(self, old_name: str, new_name: str) -> bool:
        """Renomme un membre. Retourne False si échec."""
        clean = new_name.strip()
        if not clean or clean in self._members:
            return False
        try:
            idx = self._members.index(old_name)
            self._members[idx] = clean
            self._save()
            return True
        except ValueError:
            return False

    def reorder(self, new_order: list[str]) -> None:
        """Réordonne les membres selon la liste fournie."""
        self._members = list(new_order)
        self._save()

    # ── Persistance ───────────────────────────────────────────

    def _load(self) -> None:
        """Charge la liste depuis le fichier JSON."""
        if self._file.exists():
            try:
                with open(self._file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self._members = data.get("members", [])
            except (json.JSONDecodeError, KeyError):
                self._members = []
        else:
            self._members = []

    def _save(self) -> None:
        """Sauvegarde la liste dans le fichier JSON."""
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump({"members": self._members}, f, ensure_ascii=False, indent=2)
