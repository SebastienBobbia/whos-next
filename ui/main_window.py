"""
MainWindow — Fenêtre principale de l'application Who's Next.

Gère la navigation entre les 3 vues :
  1. TeamView     — gestion de l'équipe
  2. SetupView    — sélection des présents
  3. SessionView  — session live du daily
"""

import customtkinter as ctk

from team_manager import TeamManager
from ui.team_view import TeamView
from ui.setup_view import SetupView
from ui.session_view import SessionView


class MainWindow(ctk.CTk):
    """Fenêtre principale always-on-top avec navigation entre vues."""

    def __init__(self):
        super().__init__()

        # Configuration de la fenêtre
        self.title("Who's Next?")
        self.geometry("420x550")
        self.minsize(120, 150)
        self.attributes("-topmost", True)  # always-on-top

        # Thème sombre
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        # Logique métier
        self._team = TeamManager()

        # Conteneur principal (les vues s'empilent ici)
        self._container = ctk.CTkFrame(self, fg_color="transparent")
        self._container.pack(fill="both", expand=True)

        # Créer les 3 vues
        self._team_view = TeamView(
            self._container,
            team_manager=self._team,
            on_start_session=self._show_setup,
        )
        self._setup_view = SetupView(
            self._container,
            team_manager=self._team,
            on_launch_session=self._start_session,
            on_back=self._show_team,
        )
        self._session_view = SessionView(
            self._container,
            on_end_session=self._end_session,
            get_window=lambda: self,
        )

        # Toggle always-on-top (petit bouton en bas, caché en session)
        self._topmost_var = ctk.BooleanVar(value=True)
        self._topmost_cb = ctk.CTkCheckBox(
            self,
            text="Toujours au premier plan",
            variable=self._topmost_var,
            font=ctk.CTkFont(size=10),
            height=20,
            checkbox_width=16,
            checkbox_height=16,
            command=self._toggle_topmost,
        )
        self._topmost_cb.pack(side="bottom", pady=(0, 5))

        # Démarrer sur la vue équipe
        self._show_team()

    # ── Navigation ────────────────────────────────────────────

    def _hide_all(self):
        """Cache toutes les vues."""
        self._team_view.pack_forget()
        self._setup_view.pack_forget()
        self._session_view.pack_forget()

    def _show_team(self):
        """Affiche la vue de gestion d'équipe, restaure la géométrie normale."""
        self._hide_all()
        self._topmost_cb.pack(side="bottom", pady=(0, 5))
        self.geometry("420x550")
        self.minsize(350, 450)
        self._team_view.pack(in_=self._container, fill="both", expand=True)

    def _show_setup(self):
        """Affiche la vue de sélection des présents."""
        if not self._team.members:
            return
        self._hide_all()
        self._topmost_cb.pack(side="bottom", pady=(0, 5))
        self.geometry("420x550")
        self.minsize(350, 450)
        self._setup_view.refresh()
        self._setup_view.pack(in_=self._container, fill="both", expand=True)

    def _start_session(self, attendees: list[str]):
        """Lance une session live : cache le footer, laisse SessionView gérer la géométrie."""
        self._hide_all()
        # Cacher la checkbox pendant la session (pas de place)
        self._topmost_cb.pack_forget()
        # Taille minimale compacte pour le mode session
        self.minsize(120, 100)
        self._session_view.pack(in_=self._container, fill="both", expand=True)
        self._session_view.start_session(attendees)

    def _end_session(self):
        """Termine la session et retourne à la vue équipe."""
        self._show_team()

    # ── Utilitaires ───────────────────────────────────────────

    def _toggle_topmost(self):
        """Bascule le mode always-on-top."""
        self.attributes("-topmost", self._topmost_var.get())
