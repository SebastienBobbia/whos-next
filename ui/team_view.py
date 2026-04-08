"""
TeamView — Vue de gestion des membres de l'équipe.

Fonctionnalités :
  - Ajouter / supprimer des membres
  - Associer une icône (emoji ou image) à chaque membre via IconPickerDialog
  - Réordonner les membres par glisser-déplacer (maintien + glisser)
"""

import customtkinter as ctk
from PIL import Image

from team_manager import TeamManager, Member
from ui.icon_picker import IconPickerDialog

# Taille de l'icône dans la liste
_ICON_SIZE = (24, 24)


class TeamView(ctk.CTkFrame):
    """Vue pour gérer la liste des membres de l'équipe."""

    def __init__(self, parent, team_manager: TeamManager, on_start_session):
        super().__init__(parent)
        self._team = team_manager
        self._on_start_session = on_start_session

        # Drag & drop state
        self._drag_source_index: int | None = None
        self._drag_ghost: ctk.CTkFrame | None = None
        self._drag_y_offset: int = 0
        self._drop_indicator: ctk.CTkFrame | None = None

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

        # Hint drag & drop
        self._drag_hint = ctk.CTkLabel(
            self,
            text="⠿ Maintenir et glisser pour réordonner",
            font=ctk.CTkFont(size=10),
            text_color="#6B7280",
        )
        self._drag_hint.pack(pady=(0, 2))

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

    # ── Actions membres ───────────────────────────────────────

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

    def _open_icon_picker(self, member: Member):
        """Ouvre le dialog de sélection d'icône pour un membre."""
        dlg = IconPickerDialog(
            self.winfo_toplevel(),
            current_icon_type=member["icon_type"],
            current_icon_value=member["icon_value"],
            title=f"Icône — {member['name']}",
        )
        self.winfo_toplevel().wait_window(dlg)
        if dlg.result is not None:
            icon_type, icon_value = dlg.result
            self._team.set_icon(member["name"], icon_type, icon_value)
            self._refresh_list()

    # ── Rendu liste ───────────────────────────────────────────

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
            self._drag_hint.pack_forget()
        else:
            self._drag_hint.pack(pady=(0, 2), after=self._error_label)
            for i, member in enumerate(members):
                self._build_member_row(i, member)

        self._count_label.configure(text=f"{len(members)} membre(s) dans l'équipe")

    def _build_member_row(self, index: int, member: Member):
        """Construit la ligne d'un membre dans la liste."""
        row = ctk.CTkFrame(self._list_frame, fg_color="#2a2a3e", corner_radius=6)
        row.pack(fill="x", pady=2, padx=2)

        # ── Poignée de drag ───────────────────────────────────
        handle = ctk.CTkLabel(
            row,
            text="⠿",
            font=ctk.CTkFont(size=16),
            text_color="#6B7280",
            width=24,
            cursor="fleur",
        )
        handle.pack(side="left", padx=(6, 2))

        # ── Icône ─────────────────────────────────────────────
        icon_widget = self._make_icon_widget(row, member, size=_ICON_SIZE)
        if icon_widget:
            icon_widget.pack(side="left", padx=(2, 4))

        # ── Numéro + nom ──────────────────────────────────────
        label = ctk.CTkLabel(
            row,
            text=f"{index + 1}. {member['name']}",
            font=ctk.CTkFont(size=13),
            anchor="w",
        )
        label.pack(side="left", fill="x", expand=True)

        # ── Bouton éditer icône ───────────────────────────────
        icon_btn_text = member["icon_value"] if member["icon_type"] == "emoji" else "🖼"
        if not member["icon_type"]:
            icon_btn_text = "＋"
        icon_edit_btn = ctk.CTkButton(
            row,
            text=icon_btn_text,
            width=30,
            height=25,
            font=ctk.CTkFont(size=13),
            fg_color="#374151",
            hover_color="#4B5563",
            command=lambda m=member: self._open_icon_picker(m),
        )
        icon_edit_btn.pack(side="right", padx=(2, 2))

        # ── Bouton supprimer ──────────────────────────────────
        del_btn = ctk.CTkButton(
            row,
            text="✕",
            width=30,
            height=25,
            fg_color="#CC4444",
            hover_color="#FF5555",
            font=ctk.CTkFont(size=11),
            command=lambda n=member["name"]: self._remove_member(n),
        )
        del_btn.pack(side="right", padx=(2, 6))

        # ── Bindings drag & drop ──────────────────────────────
        for widget in (row, handle, label):
            widget.bind("<ButtonPress-1>", lambda e, i=index: self._drag_start(e, i))
            widget.bind("<B1-Motion>", lambda e, i=index: self._drag_motion(e, i))
            widget.bind("<ButtonRelease-1>", lambda e: self._drag_end(e))

    def _make_icon_widget(self, parent, member: Member, size=(24, 24)):
        """Crée le widget d'icône approprié selon le type."""
        if member["icon_type"] == "emoji" and member["icon_value"]:
            return ctk.CTkLabel(
                parent,
                text=member["icon_value"],
                font=ctk.CTkFont(size=size[0] - 4),
                width=size[0],
            )
        elif member["icon_type"] == "image":
            img_path = self._team.get_icon_path(member)
            if img_path:
                try:
                    pil_img = Image.open(img_path).convert("RGBA")
                    ctk_img = ctk.CTkImage(pil_img, size=size)
                    lbl = ctk.CTkLabel(parent, image=ctk_img, text="", width=size[0])
                    lbl._ctk_image_ref = ctk_img  # garder une référence
                    return lbl
                except Exception:
                    pass
        return None

    # ── Drag & Drop ───────────────────────────────────────────

    def _drag_start(self, event, index: int):
        """Démarre le drag sur la ligne d'index donné."""
        self._drag_source_index = index
        self._drag_y_offset = event.y_root

    def _drag_motion(self, event, source_index: int):
        """Gère le déplacement pendant le drag."""
        if self._drag_source_index is None:
            return

        rows = self._get_row_widgets()
        if not rows:
            return

        # Calculer l'index cible à partir de la position Y de la souris
        target_index = self._compute_drop_index(event.y_root, rows)
        if target_index is None:
            return

        # Feedback visuel : mettre en évidence la rangée source
        for i, row in enumerate(rows):
            if i == self._drag_source_index:
                row.configure(fg_color="#1a5c2a")
            else:
                row.configure(fg_color="#2a2a3e")

        # Indicateur de position de drop
        self._show_drop_indicator(target_index, rows)

    def _drag_end(self, event):
        """Termine le drag et applique le réordonnement."""
        if self._drag_source_index is None:
            return

        rows = self._get_row_widgets()
        target_index = self._compute_drop_index(event.y_root, rows)

        # Réinitialiser le feedback visuel
        for row in rows:
            row.configure(fg_color="#2a2a3e")
        self._hide_drop_indicator()

        src = self._drag_source_index
        self._drag_source_index = None

        if target_index is None or target_index == src:
            return

        # Appliquer le nouvel ordre
        members = self._team.members
        names = [m["name"] for m in members]
        name = names.pop(src)
        # Ajuster l'index cible après suppression de la source
        insert_at = target_index if target_index < src else target_index - 1
        names.insert(insert_at, name)
        self._team.reorder(names)
        self._refresh_list()

    def _get_row_widgets(self) -> list[ctk.CTkFrame]:
        """Retourne les widgets ligne (CTkFrame) dans l'ordre d'affichage."""
        return [
            w for w in self._list_frame.winfo_children() if isinstance(w, ctk.CTkFrame)
        ]

    def _compute_drop_index(self, y_root: int, rows: list) -> int | None:
        """Calcule l'index de dépôt selon la position Y absolue de la souris."""
        if not rows:
            return None

        for i, row in enumerate(rows):
            ry = row.winfo_rooty()
            rh = row.winfo_height()
            mid = ry + rh // 2
            if y_root < mid:
                return i

        return len(rows)

    def _show_drop_indicator(self, target_index: int, rows: list):
        """Affiche un trait horizontal indiquant où sera insérée la ligne."""
        self._hide_drop_indicator()
        if not rows:
            return

        # On insère un frame fin comme indicateur dans le scrollable frame
        indicator = ctk.CTkFrame(
            self._list_frame,
            height=3,
            fg_color="#4ADE80",
            corner_radius=0,
        )
        self._drop_indicator = indicator

        if target_index >= len(rows):
            indicator.pack(fill="x", padx=2)
        else:
            indicator.pack(fill="x", padx=2, before=rows[target_index])

    def _hide_drop_indicator(self):
        """Supprime l'indicateur de drop."""
        if self._drop_indicator is not None:
            try:
                self._drop_indicator.destroy()
            except Exception:
                pass
            self._drop_indicator = None

    # ── Utilitaires ───────────────────────────────────────────

    def _show_error(self, msg: str):
        """Affiche un message d'erreur."""
        self._error_label.configure(text=msg)

    def _clear_error(self):
        """Efface le message d'erreur."""
        self._error_label.configure(text="")
