"""
Team Manager — Gestion des membres de l'équipe avec persistance JSON.

Stockage persistant :
  - Windows : %APPDATA%\\WhosNext\\team.json
  - Linux/Mac : ~/.whonext/team.json

Format JSON v2 :
  {
    "version": 2,
    "members": [
      {"name": "Alice", "icon_type": "emoji", "icon_value": "🐱"},
      {"name": "Bob",   "icon_type": "image", "icon_value": "bob.png"},
      {"name": "Charlie", "icon_type": "", "icon_value": ""}
    ]
  }

Rétrocompatibilité : l'ancien format v1 (liste de strings) est migré
automatiquement au premier chargement.
"""

import json
import os
import shutil
import sys
from pathlib import Path
from typing import TypedDict


class Member(TypedDict):
    """Représente un membre de l'équipe."""
    name: str
    icon_type: str   # "emoji" | "image" | ""
    icon_value: str  # emoji char ou nom de fichier relatif au dossier data


class TeamManager:
    """Gère la liste des membres de l'équipe (ajout, suppression, persistance)."""

    def __init__(self, data_path: str | None = None):
        if data_path is None:
            self._data_dir = self._resolve_data_dir()
        else:
            self._data_dir = Path(data_path)

        self._data_dir.mkdir(parents=True, exist_ok=True)
        # Sous-dossier pour les images uploadées
        self._icons_dir = self._data_dir / "icons"
        self._icons_dir.mkdir(parents=True, exist_ok=True)

        self._file = self._data_dir / "team.json"
        self._members: list[Member] = []
        self._load()

    @staticmethod
    def _resolve_data_dir() -> Path:
        """
        Résout le répertoire de données persistant selon l'OS.
        - Windows : %APPDATA%\\WhosNext\\
        - Linux/Mac : ~/.whonext/
        Garantit que les données survivent entre les relances de l'exe PyInstaller.
        """
        if sys.platform == "win32":
            appdata = os.environ.get("APPDATA")
            if appdata:
                return Path(appdata) / "WhosNext"
        return Path.home() / ".whonext"

    # ── Public API ────────────────────────────────────────────

    @property
    def members(self) -> list[Member]:
        """Retourne une copie de la liste des membres (objets Member)."""
        return [dict(m) for m in self._members]  # type: ignore[return-value]

    @property
    def names(self) -> list[str]:
        """Retourne uniquement les noms des membres (compat session)."""
        return [m["name"] for m in self._members]

    def get_member(self, name: str) -> Member | None:
        """Retourne le membre correspondant au nom, ou None."""
        for m in self._members:
            if m["name"] == name:
                return dict(m)  # type: ignore[return-value]
        return None

    def add_member(self, name: str, icon_type: str = "", icon_value: str = "") -> bool:
        """Ajoute un membre. Retourne False si le nom existe déjà."""
        clean = name.strip()
        if not clean:
            return False
        if any(m["name"] == clean for m in self._members):
            return False
        self._members.append(
            Member(name=clean, icon_type=icon_type, icon_value=icon_value)
        )
        self._save()
        return True

    def remove_member(self, name: str) -> bool:
        """Supprime un membre. Retourne False si introuvable."""
        for i, m in enumerate(self._members):
            if m["name"] == name:
                # Supprimer l'icône image si présente
                if m["icon_type"] == "image" and m["icon_value"]:
                    self._delete_icon_file(m["icon_value"])
                self._members.pop(i)
                self._save()
                return True
        return False

    def rename_member(self, old_name: str, new_name: str) -> bool:
        """Renomme un membre. Retourne False si échec."""
        clean = new_name.strip()
        if not clean or any(m["name"] == clean for m in self._members):
            return False
        for m in self._members:
            if m["name"] == old_name:
                m["name"] = clean
                self._save()
                return True
        return False

    def set_icon(self, name: str, icon_type: str, icon_value: str) -> bool:
        """
        Définit l'icône d'un membre.

        Args:
            name:       nom du membre
            icon_type:  "emoji" | "image" | ""
            icon_value: caractère emoji, ou chemin source absolu vers l'image
                        (sera copiée dans le dossier icons/)

        Returns:
            True si succès, False si membre introuvable.
        """
        for m in self._members:
            if m["name"] == name:
                # Supprimer l'ancienne icône image si on la remplace
                if m["icon_type"] == "image" and m["icon_value"]:
                    self._delete_icon_file(m["icon_value"])

                if icon_type == "image" and icon_value:
                    # Copier le fichier dans icons/ et ne stocker que le nom
                    filename = self._copy_icon(icon_value)
                    m["icon_type"] = "image"
                    m["icon_value"] = filename
                else:
                    m["icon_type"] = icon_type
                    m["icon_value"] = icon_value

                self._save()
                return True
        return False

    def clear_icon(self, name: str) -> bool:
        """Supprime l'icône d'un membre."""
        return self.set_icon(name, "", "")

    def get_icon_path(self, member: Member) -> Path | None:
        """Retourne le Path absolu vers l'image, ou None si pas d'icône image."""
        if member["icon_type"] == "image" and member["icon_value"]:
            p = self._icons_dir / member["icon_value"]
            return p if p.exists() else None
        return None

    def reorder(self, new_order: list[str]) -> None:
        """Réordonne les membres selon la liste de noms fournie."""
        by_name = {m["name"]: m for m in self._members}
        self._members = [by_name[n] for n in new_order if n in by_name]
        self._save()

    # ── Persistance ───────────────────────────────────────────

    def _load(self) -> None:
        """Charge la liste depuis le fichier JSON (avec migration v1→v2)."""
        if not self._file.exists():
            self._members = []
            return
        try:
            with open(self._file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Détection du format
            if isinstance(data, dict) and data.get("version") == 2:
                # Format v2 natif
                raw = data.get("members", [])
                self._members = [
                    Member(
                        name=m.get("name", ""),
                        icon_type=m.get("icon_type", ""),
                        icon_value=m.get("icon_value", ""),
                    )
                    for m in raw
                    if m.get("name")
                ]
            else:
                # Format v1 : {"members": ["Alice", "Bob", ...]}
                old_list = data.get("members", [])
                self._members = [
                    Member(name=n, icon_type="", icon_value="")
                    for n in old_list
                    if isinstance(n, str) and n
                ]
                # Migration immédiate vers v2
                self._save()

        except (json.JSONDecodeError, KeyError, TypeError):
            self._members = []

    def _save(self) -> None:
        """Sauvegarde la liste dans le fichier JSON (format v2)."""
        with open(self._file, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "version": 2,
                    "members": list(self._members),
                },
                f,
                ensure_ascii=False,
                indent=2,
            )

    # ── Gestion fichiers icônes ───────────────────────────────

    def _copy_icon(self, source_path: str) -> str:
        """Copie un fichier image dans icons/ et retourne son nom de fichier."""
        src = Path(source_path)
        # Nom unique basé sur le nom original + suffix numérique si collision
        dest_name = src.name
        dest = self._icons_dir / dest_name
        counter = 1
        while dest.exists():
            dest_name = f"{src.stem}_{counter}{src.suffix}"
            dest = self._icons_dir / dest_name
            counter += 1
        shutil.copy2(src, dest)
        return dest_name

    def _delete_icon_file(self, filename: str) -> None:
        """Supprime un fichier icône du dossier icons/ si présent."""
        try:
            (self._icons_dir / filename).unlink(missing_ok=True)
        except OSError:
            pass
