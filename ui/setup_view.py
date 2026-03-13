"""
SetupView — Vue de sélection des participants présents au daily.

Affiche tous les membres avec des checkboxes pour cocher qui est présent.
"""

import customtkinter as ctk

from team_manager import TeamManager


class SetupView(ctk.CTkFrame):
    """Vue pour sélectionner les personnes présentes au meeting."""

    def __init__(
        self, parent, team_manager: TeamManager, on_launch_session, on_back
    ):
        super().__init__(parent)
        self._team = team_manager
        self._on_launch_session = on_launch_session
        self._on_back = on_back
        self._checkboxes: dict[str, ctk.BooleanVar] = {}

        self._build_ui()

    def _build_ui(self):
        """Construit l'interface de la vue."""
        # Titre
        title = ctk.CTkLabel(
            self,
            text="Qui est présent ?",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        title.pack(pady=(15, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Cochez les personnes présentes au daily",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        subtitle.pack(pady=(0, 10))

        # Boutons tout cocher / tout décocher
        toggle_frame = ctk.CTkFrame(self, fg_color="transparent")
        toggle_frame.pack(fill="x", padx=20, pady=(0, 5))

        ctk.CTkButton(
            toggle_frame,
            text="Tout cocher",
            width=100,
            height=28,
            font=ctk.CTkFont(size=11),
            command=self._check_all,
        ).pack(side="left", padx=(0, 5))

        ctk.CTkButton(
            toggle_frame,
            text="Tout décocher",
            width=100,
            height=28,
            font=ctk.CTkFont(size=11),
            fg_color="gray",
            command=self._uncheck_all,
        ).pack(side="left")

        # Liste des checkboxes (scrollable)
        self._list_frame = ctk.CTkScrollableFrame(
            self, label_text="Membres de l'équipe"
        )
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=(5, 10))

        # Compteur de sélection
        self._count_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self._count_label.pack(pady=(0, 10))

        # Boutons bas
        btn_frame = ctk.CTkFrame(self, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkButton(
            btn_frame,
            text="<<< Retour",
            width=100,
            fg_color="gray",
            hover_color="#555555",
            command=self._on_back,
        ).pack(side="left")

        self._start_btn = ctk.CTkButton(
            btn_frame,
            text="Démarrer le Daily >>>",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._launch,
        )
        self._start_btn.pack(side="right", fill="x", expand=True, padx=(10, 0))

    def refresh(self):
        """Rafraîchit la liste des checkboxes depuis le TeamManager."""
        # Nettoyer
        for widget in self._list_frame.winfo_children():
            widget.destroy()
        self._checkboxes.clear()

        members = self._team.members

        if not members:
            ctk.CTkLabel(
                self._list_frame,
                text="Aucun membre dans l'équipe.\nRetournez en arrière pour en ajouter.",
                text_color="gray",
            ).pack(pady=20)
            self._start_btn.configure(state="disabled")
            return

        self._start_btn.configure(state="normal")

        for name in members:
            var = ctk.BooleanVar(value=True)  # coché par défaut
            var.trace_add("write", lambda *_: self._update_count())
            self._checkboxes[name] = var

            cb = ctk.CTkCheckBox(
                self._list_frame,
                text=name,
                variable=var,
                font=ctk.CTkFont(size=13),
            )
            cb.pack(fill="x", pady=3, padx=5)

        self._update_count()

    def _check_all(self):
        for var in self._checkboxes.values():
            var.set(True)

    def _uncheck_all(self):
        for var in self._checkboxes.values():
            var.set(False)

    def _update_count(self):
        checked = sum(1 for v in self._checkboxes.values() if v.get())
        total = len(self._checkboxes)
        self._count_label.configure(text=f"{checked}/{total} présent(s)")

    def _get_attendees(self) -> list[str]:
        """Retourne la liste des noms cochés."""
        return [name for name, var in self._checkboxes.items() if var.get()]

    def _launch(self):
        """Lance la session avec les personnes sélectionnées."""
        attendees = self._get_attendees()
        if not attendees:
            return
        self._on_launch_session(attendees)
