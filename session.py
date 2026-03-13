"""
Session — Logique métier d'une session de daily meeting.

Gère la liste des participants présents, qui a parlé, qui reste,
et le tirage aléatoire du prochain intervenant.
"""

import random


class Session:
    """Représente une session de daily meeting en cours."""

    def __init__(self, attendees: list[str]):
        """
        Initialise la session avec la liste des présents.

        Args:
            attendees: noms des personnes présentes au meeting.
        """
        self._attendees: list[str] = list(attendees)
        self._spoken: list[str] = []  # ordre dans lequel ils ont parlé

    # ── Propriétés ────────────────────────────────────────────

    @property
    def attendees(self) -> list[str]:
        """Tous les participants de la session."""
        return list(self._attendees)

    @property
    def spoken(self) -> list[str]:
        """Participants qui ont déjà parlé (dans l'ordre)."""
        return list(self._spoken)

    @property
    def remaining(self) -> list[str]:
        """Participants qui n'ont pas encore parlé."""
        return [a for a in self._attendees if a not in self._spoken]

    @property
    def total(self) -> int:
        """Nombre total de participants."""
        return len(self._attendees)

    @property
    def spoken_count(self) -> int:
        """Nombre de personnes ayant parlé."""
        return len(self._spoken)

    @property
    def is_complete(self) -> bool:
        """True si tout le monde a parlé."""
        return self.spoken_count == self.total

    # ── Actions ───────────────────────────────────────────────

    def mark_spoken(self, name: str) -> bool:
        """
        Marque une personne comme ayant parlé.

        Args:
            name: nom du participant.

        Returns:
            True si réussi, False si déjà parlé ou introuvable.
        """
        if name not in self._attendees or name in self._spoken:
            return False
        self._spoken.append(name)
        return True

    def unmark_spoken(self, name: str) -> bool:
        """
        Annule le marquage d'une personne (elle n'a finalement pas parlé).

        Args:
            name: nom du participant.

        Returns:
            True si réussi, False si pas dans la liste spoken.
        """
        try:
            self._spoken.remove(name)
            return True
        except ValueError:
            return False

    def pick_random(self) -> str | None:
        """
        Tire au sort un participant parmi ceux qui n'ont pas encore parlé
        et le marque automatiquement comme ayant parlé.

        Returns:
            Le nom du participant tiré, ou None si tout le monde a parlé.
        """
        remaining = self.remaining
        if not remaining:
            return None
        chosen = random.choice(remaining)
        self._spoken.append(chosen)
        return chosen

    def reset(self) -> None:
        """Remet la session à zéro (personne n'a parlé)."""
        self._spoken.clear()
