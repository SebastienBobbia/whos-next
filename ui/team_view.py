"""
TeamView — Vue de gestion des membres de l'équipe.

Permet d'ajouter, supprimer et visualiser les membres permanents.
"""

import customtkinter as ctk

from team_manager import TeamManager


class TeamView(ctk.CTkFrame):
    """Vue pour gérer la liste des membres de l'équipe."""

    def __init__(self, parent, team_manager: TeamManager, on_start_session):
        super().__init__(parent)
        self._team = team_manager
        self._on_start_session = on_start_session

        self._build_ui()
        self._refresh_list()

    def _build_ui(self):
        """Construit l'interface de la vue."""
        # Titre
        title = ctk.CTkLabel(
            self, text="Gestion de l'équipe", font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=(15, 5))

        subtitle = ctk.CTkLabel(
            self,
            text="Ajoutez les membres permanents de votre équipe",
            font=ctk.CTkFont(size=12),
            text_color="gray",
        )
        subtitle.pack(pady=(0, 15))

        # Zone de saisie + bouton ajouter
        input_frame = ctk.CTkFrame(self, fg_color="transparent")
        input_frame.pack(fill="x", padx=20, pady=(0, 10))

        self._name_entry = ctk.CTkEntry(
            input_frame, placeholder_text="Nom du membre..."
        )
        self._name_entry.pack(side="left", fill="x", expand=True, padx=(0, 8))
        self._name_entry.bind("<Return>", lambda e: self._add_member())

        add_btn = ctk.CTkButton(
            input_frame, text="Ajouter", width=90, command=self._add_member
        )
        add_btn.pack(side="right")

        # Message d'erreur
        self._error_label = ctk.CTkLabel(
            self, text="", text_color="#FF6B6B", font=ctk.CTkFont(size=11)
        )
        self._error_label.pack(pady=(0, 5))

        # Liste des membres (scrollable)
        self._list_frame = ctk.CTkScrollableFrame(self, label_text="Membres")
        self._list_frame.pack(fill="both", expand=True, padx=20, pady=(0, 10))

        # Compteur
        self._count_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=12), text_color="gray"
        )
        self._count_label.pack(pady=(0, 10))

        # Bouton démarrer la session
        start_btn = ctk.CTkButton(
            self,
            text="Préparer le Daily  >>>",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self._on_start_session,
        )
        start_btn.pack(pady=(0, 20), padx=20, fill="x")

    def _add_member(self):
        """Ajoute un membre depuis le champ de saisie."""
        name = self._name_entry.get().strip()
        if not name:
            self._show_error("Veuillez entrer un nom.")
            return

        if self._team.add_member(name):
            self._name_entry.delete(0, "end")
            self._clear_error()
            self._refresh_list()
        else:
            self._show_error(f'"{name}" existe déjà dans l\'équipe.')

    def _remove_member(self, name: str):
        """Supprime un membre de l'équipe."""
        self._team.remove_member(name)
        self._refresh_list()

    def _refresh_list(self):
        """Rafraîchit l'affichage de la liste des membres."""
        # Nettoyer la liste actuelle
        for widget in self._list_frame.winfo_children():
            widget.destroy()

        members = self._team.members

        if not members:
            empty_label = ctk.CTkLabel(
                self._list_frame,
                text="Aucun membre. Ajoutez des personnes ci-dessus.",
                text_color="gray",
            )
            empty_label.pack(pady=20)
        else:
            for i, name in enumerate(members):
                row = ctk.CTkFrame(self._list_frame, fg_color="transparent")
                row.pack(fill="x", pady=2)

                # Numéro + nom
                label = ctk.CTkLabel(
                    row,
                    text=f"  {i + 1}. {name}",
                    font=ctk.CTkFont(size=13),
                    anchor="w",
                )
                label.pack(side="left", fill="x", expand=True)

                # Bouton supprimer
                del_btn = ctk.CTkButton(
                    row,
                    text="X",
                    width=30,
                    height=25,
                    fg_color="#CC4444",
                    hover_color="#FF5555",
                    font=ctk.CTkFont(size=11),
                    command=lambda n=name: self._remove_member(n),
                )
                del_btn.pack(side="right", padx=5)

        self._count_label.configure(text=f"{len(members)} membre(s) dans l'équipe")

    def _show_error(self, msg: str):
        """Affiche un message d'erreur."""
        self._error_label.configure(text=msg)

    def _clear_error(self):
        """Efface le message d'erreur."""
        self._error_label.configure(text="")
