"""
SessionView — Vue live du daily meeting.

Affiche en temps réel qui a parlé et qui reste,
avec tirage aléatoire et marquage manuel.
"""

import customtkinter as ctk

from session import Session


class SessionView(ctk.CTkFrame):
    """Vue principale pendant le déroulement du daily meeting."""

    def __init__(self, parent, on_end_session):
        super().__init__(parent)
        self._session: Session | None = None
        self._on_end_session = on_end_session
        self._last_picked: str | None = None

        self._build_ui()

    def _build_ui(self):
        """Construit l'interface de la vue."""
        # Titre
        self._title = ctk.CTkLabel(
            self,
            text="Daily en cours",
            font=ctk.CTkFont(size=20, weight="bold"),
        )
        self._title.pack(pady=(15, 5))

        # Barre de progression texte
        self._progress_label = ctk.CTkLabel(
            self, text="", font=ctk.CTkFont(size=14, weight="bold")
        )
        self._progress_label.pack(pady=(0, 5))

        # Barre de progression visuelle
        self._progress_bar = ctk.CTkProgressBar(self)
        self._progress_bar.pack(fill="x", padx=20, pady=(0, 10))
        self._progress_bar.set(0)

        # Annonce du tirage aléatoire
        self._announce_frame = ctk.CTkFrame(self, fg_color="#1a5c2a", corner_radius=10)
        self._announce_frame.pack(fill="x", padx=20, pady=(0, 10))

        self._announce_label = ctk.CTkLabel(
            self._announce_frame,
            text="",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#4ADE80",
        )
        self._announce_label.pack(pady=10, padx=10)
        self._announce_frame.pack_forget()  # caché par défaut

        # Zone principale : deux colonnes
        main_frame = ctk.CTkFrame(self, fg_color="transparent")
        main_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(0, weight=1)

        # Colonne gauche : n'ont pas encore parlé
        self._remaining_frame = ctk.CTkScrollableFrame(
            main_frame, label_text="N'ont pas encore parlé"
        )
        self._remaining_frame.grid(row=0, column=0, sticky="nsew", padx=(5, 3))

        # Colonne droite : ont parlé
        self._spoken_frame = ctk.CTkScrollableFrame(
            main_frame, label_text="Ont parlé"
        )
        self._spoken_frame.grid(row=0, column=1, sticky="nsew", padx=(3, 5))

        # Boutons d'action
        action_frame = ctk.CTkFrame(self, fg_color="transparent")
        action_frame.pack(fill="x", padx=15, pady=(5, 10))

        self._random_btn = ctk.CTkButton(
            action_frame,
            text="Tirer au sort",
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
            fg_color="#2563EB",
            hover_color="#1D4ED8",
            command=self._pick_random,
        )
        self._random_btn.pack(fill="x", pady=(0, 8))

        bottom_frame = ctk.CTkFrame(action_frame, fg_color="transparent")
        bottom_frame.pack(fill="x")

        ctk.CTkButton(
            bottom_frame,
            text="Reset",
            width=100,
            fg_color="#6B7280",
            hover_color="#4B5563",
            command=self._reset_session,
        ).pack(side="left")

        ctk.CTkButton(
            bottom_frame,
            text="Terminer le Daily",
            width=140,
            fg_color="#DC2626",
            hover_color="#B91C1C",
            command=self._on_end_session,
        ).pack(side="right")

    def start_session(self, attendees: list[str]):
        """Démarre une nouvelle session avec les participants donnés."""
        self._session = Session(attendees)
        self._last_picked = None
        self._refresh()

    def _pick_random(self):
        """Tire au sort le prochain intervenant."""
        if self._session is None or self._session.is_complete:
            return
        chosen = self._session.pick_random()
        if chosen:
            self._last_picked = chosen
            self._refresh()

    def _mark_spoken(self, name: str):
        """Marque manuellement une personne comme ayant parlé."""
        if self._session is None:
            return
        self._session.mark_spoken(name)
        self._refresh()

    def _unmark_spoken(self, name: str):
        """Annule le marquage d'une personne."""
        if self._session is None:
            return
        self._session.unmark_spoken(name)
        self._last_picked = None
        self._refresh()

    def _reset_session(self):
        """Remet tous les participants comme n'ayant pas parlé."""
        if self._session is None:
            return
        self._session.reset()
        self._last_picked = None
        self._refresh()

    def _refresh(self):
        """Met à jour l'affichage complet de la session."""
        if self._session is None:
            return

        # Progression
        spoken = self._session.spoken_count
        total = self._session.total
        self._progress_label.configure(text=f"{spoken} / {total} ont parlé")

        progress = spoken / total if total > 0 else 0
        self._progress_bar.set(progress)

        # Annonce tirage
        if self._last_picked:
            self._announce_frame.pack(fill="x", padx=20, pady=(0, 10),
                                       after=self._progress_bar)
            self._announce_label.configure(
                text=f">>> {self._last_picked} <<<"
            )
        else:
            self._announce_frame.pack_forget()

        # Message fin
        if self._session.is_complete:
            self._title.configure(text="Daily terminé !")
            self._random_btn.configure(state="disabled", text="Tout le monde a parlé")
        else:
            self._title.configure(text="Daily en cours")
            self._random_btn.configure(state="normal", text="Tirer au sort")

        # Liste "N'ont pas encore parlé"
        for widget in self._remaining_frame.winfo_children():
            widget.destroy()

        remaining = self._session.remaining
        if not remaining:
            ctk.CTkLabel(
                self._remaining_frame,
                text="Tout le monde a parlé !",
                text_color="#4ADE80",
                font=ctk.CTkFont(size=12),
            ).pack(pady=10)
        else:
            for name in remaining:
                btn = ctk.CTkButton(
                    self._remaining_frame,
                    text=name,
                    height=35,
                    font=ctk.CTkFont(size=13),
                    fg_color="#374151",
                    hover_color="#4B5563",
                    anchor="w",
                    command=lambda n=name: self._mark_spoken(n),
                )
                btn.pack(fill="x", pady=2, padx=5)

        # Liste "Ont parlé"
        for widget in self._spoken_frame.winfo_children():
            widget.destroy()

        spoken_list = self._session.spoken
        if not spoken_list:
            ctk.CTkLabel(
                self._spoken_frame,
                text="Personne n'a encore parlé",
                text_color="gray",
                font=ctk.CTkFont(size=12),
            ).pack(pady=10)
        else:
            for i, name in enumerate(spoken_list, 1):
                row = ctk.CTkFrame(self._spoken_frame, fg_color="transparent")
                row.pack(fill="x", pady=2, padx=5)

                ctk.CTkLabel(
                    row,
                    text=f"  {i}. {name}",
                    font=ctk.CTkFont(size=13),
                    text_color="#9CA3AF",
                    anchor="w",
                ).pack(side="left", fill="x", expand=True)

                # Bouton annuler
                ctk.CTkButton(
                    row,
                    text="Annuler",
                    width=55,
                    height=24,
                    font=ctk.CTkFont(size=10),
                    fg_color="#6B7280",
                    hover_color="#9CA3AF",
                    command=lambda n=name: self._unmark_spoken(n),
                ).pack(side="right")
