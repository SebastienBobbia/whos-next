"""
IconPickerDialog — Dialog de sélection d'icône pour un membre de l'équipe.

Permet de choisir :
  - Un emoji parmi une grille prédéfinie
  - Un fichier image PNG/JPG depuis le disque
  - Supprimer l'icône courante
"""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

# ── Palette d'emojis proposés ─────────────────────────────────
EMOJI_GRID = [
    # Visages
    "😀", "😎", "🤓", "😍", "🤩", "😜", "🥸", "🧐",
    "😇", "🤠", "🥳", "😈", "👻", "🤖", "👽", "🎃",
    # Animaux
    "🐱", "🐶", "🦊", "🐻", "🐼", "🐨", "🐯", "🦁",
    "🐸", "🐵", "🦄", "🐲", "🦋", "🐧", "🦉", "🦅",
    # Professions / objets
    "👨‍💻", "👩‍💻", "🧑‍🚀", "👨‍🎨", "👩‍🔬", "🧑‍🍳", "👨‍🎤", "🧑‍🏫",
    "⚡", "🔥", "💎", "🌟", "🎯", "🚀", "🎸", "🎮",
    # Nature
    "🌈", "☀️",  "🌙", "⭐", "❄️",  "🌊", "🌸", "🍀",
    # Divers
    "❤️",  "💙", "💜", "🖤", "🤍", "💛", "🧡", "💚",
]

_BG_DARK    = "#1e1e2e"
_BG_CARD    = "#2d2d44"
_BG_HOVER   = "#3d3d5c"
_BG_SEL     = "#1a5c2a"
_BORDER_SEL = "#4ADE80"
_TXT        = "#e0e0e0"
_TXT_GRAY   = "#9CA3AF"


class IconPickerDialog(ctk.CTkToplevel):
    """
    Dialog modal de sélection d'icône.

    Usage :
        dlg = IconPickerDialog(parent, current_icon_type, current_icon_value)
        parent.wait_window(dlg)
        if dlg.result is not None:
            icon_type, icon_value = dlg.result
    """

    def __init__(
        self,
        parent,
        current_icon_type: str = "",
        current_icon_value: str = "",
        title: str = "Choisir une icône",
    ):
        super().__init__(parent)
        self.title(title)
        self.resizable(False, False)
        self.grab_set()        # modal
        self.focus_set()

        self.result: tuple[str, str] | None = None
        self._selected_emoji: str | None = None
        self._selected_file: str | None = None
        self._emoji_buttons: dict[str, ctk.CTkButton] = {}

        # Pré-sélection depuis l'état courant
        if current_icon_type == "emoji":
            self._selected_emoji = current_icon_value
        elif current_icon_type == "image":
            self._selected_file = current_icon_value  # nom de fichier seul (affiché)

        self._build_ui()
        self._center_on_parent(parent)

    def _build_ui(self):
        self.configure(fg_color=_BG_DARK)

        # ── Titre ─────────────────────────────────────────────
        ctk.CTkLabel(
            self,
            text="Choisir une icône",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color=_TXT,
        ).pack(pady=(16, 4), padx=20)

        ctk.CTkLabel(
            self,
            text="Sélectionnez un emoji ou importez une image",
            font=ctk.CTkFont(size=11),
            text_color=_TXT_GRAY,
        ).pack(pady=(0, 12), padx=20)

        # ── Grille d'emojis ───────────────────────────────────
        grid_outer = ctk.CTkScrollableFrame(
            self,
            label_text="Emojis",
            width=340,
            height=220,
            fg_color=_BG_CARD,
        )
        grid_outer.pack(padx=16, pady=(0, 10), fill="x")

        COLS = 8
        for idx, emoji in enumerate(EMOJI_GRID):
            row = idx // COLS
            col = idx % COLS
            is_sel = (emoji == self._selected_emoji)
            btn = ctk.CTkButton(
                grid_outer,
                text=emoji,
                width=36,
                height=36,
                font=ctk.CTkFont(size=18),
                fg_color=_BG_SEL if is_sel else _BG_CARD,
                hover_color=_BG_HOVER,
                corner_radius=6,
                border_width=2 if is_sel else 0,
                border_color=_BORDER_SEL if is_sel else _BG_CARD,
                command=lambda e=emoji: self._select_emoji(e),
            )
            btn.grid(row=row, column=col, padx=2, pady=2, sticky="nsew")
            self._emoji_buttons[emoji] = btn

        # ── Image depuis le disque ────────────────────────────
        img_frame = ctk.CTkFrame(self, fg_color=_BG_CARD, corner_radius=8)
        img_frame.pack(padx=16, pady=(0, 10), fill="x")

        ctk.CTkLabel(
            img_frame,
            text="Image personnalisée",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color=_TXT,
            anchor="w",
        ).pack(side="left", padx=12, pady=10)

        self._file_label = ctk.CTkLabel(
            img_frame,
            text=self._selected_file or "Aucun fichier",
            font=ctk.CTkFont(size=10),
            text_color=_TXT_GRAY,
            anchor="w",
        )
        self._file_label.pack(side="left", fill="x", expand=True, padx=4)

        ctk.CTkButton(
            img_frame,
            text="Parcourir…",
            width=90,
            height=28,
            font=ctk.CTkFont(size=11),
            command=self._browse_file,
        ).pack(side="right", padx=10, pady=8)

        # ── Boutons bas ───────────────────────────────────────
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(padx=16, pady=(0, 16), fill="x")

        ctk.CTkButton(
            btn_row,
            text="Supprimer l'icône",
            width=110,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color="#7f1d1d",
            hover_color="#DC2626",
            command=self._clear_icon,
        ).pack(side="left")

        ctk.CTkButton(
            btn_row,
            text="Annuler",
            width=80,
            height=32,
            font=ctk.CTkFont(size=11),
            fg_color="#374151",
            hover_color="#4B5563",
            command=self.destroy,
        ).pack(side="right", padx=(8, 0))

        ctk.CTkButton(
            btn_row,
            text="Valider",
            width=80,
            height=32,
            font=ctk.CTkFont(size=11),
            command=self._confirm,
        ).pack(side="right")

    # ── Actions ───────────────────────────────────────────────

    def _select_emoji(self, emoji: str):
        """Sélectionne un emoji et désélectionne le fichier image."""
        # Déselectionner l'ancien
        if self._selected_emoji and self._selected_emoji in self._emoji_buttons:
            old_btn = self._emoji_buttons[self._selected_emoji]
            old_btn.configure(fg_color=_BG_CARD, border_width=0, border_color=_BG_CARD)

        # Sélectionner le nouveau (toggle si même emoji)
        if self._selected_emoji == emoji:
            self._selected_emoji = None
        else:
            self._selected_emoji = emoji
            btn = self._emoji_buttons[emoji]
            btn.configure(fg_color=_BG_SEL, border_width=2, border_color=_BORDER_SEL)

        # Effacer la sélection fichier
        self._selected_file = None
        self._file_label.configure(text="Aucun fichier")

    def _browse_file(self):
        """Ouvre un dialogue de sélection de fichier image."""
        path = filedialog.askopenfilename(
            title="Choisir une image",
            filetypes=[
                ("Images", "*.png *.jpg *.jpeg *.gif *.bmp *.webp"),
                ("Tous les fichiers", "*.*"),
            ],
        )
        if not path:
            return

        self._selected_file = path
        # Afficher uniquement le nom du fichier (tronqué si long)
        display = Path(path).name
        if len(display) > 28:
            display = display[:25] + "…"
        self._file_label.configure(text=display)

        # Désélectionner l'emoji
        if self._selected_emoji and self._selected_emoji in self._emoji_buttons:
            old_btn = self._emoji_buttons[self._selected_emoji]
            old_btn.configure(fg_color=_BG_CARD, border_width=0, border_color=_BG_CARD)
        self._selected_emoji = None

    def _clear_icon(self):
        """Supprime l'icône (retourne ("", ""))."""
        self.result = ("", "")
        self.destroy()

    def _confirm(self):
        """Valide la sélection et ferme le dialog."""
        if self._selected_file:
            self.result = ("image", self._selected_file)
        elif self._selected_emoji:
            self.result = ("emoji", self._selected_emoji)
        else:
            # Rien sélectionné → pas de changement (result reste None)
            pass
        self.destroy()

    # ── Utilitaires ───────────────────────────────────────────

    def _center_on_parent(self, parent):
        """Centre le dialog sur la fenêtre parente."""
        self.update_idletasks()
        pw = parent.winfo_rootx()
        py = parent.winfo_rooty()
        pW = parent.winfo_width()
        pH = parent.winfo_height()
        dW = self.winfo_width()
        dH = self.winfo_height()
        x = pw + (pW - dW) // 2
        y = py + (pH - dH) // 2
        self.geometry(f"+{x}+{y}")
