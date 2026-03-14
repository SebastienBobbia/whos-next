"""
SessionView — Vue live du daily meeting.

Design compact, deux modes :
  - VERTICAL   : fenêtre collée au bord droit, largeur 7% écran, 100% hauteur
  - HORIZONTAL : fenêtre collée au bord haut, pleine largeur

Seuls les participants qui n'ont pas encore parlé sont affichés.
Cliquer sur un nom le fait disparaître (= a parlé).
Tirage aléatoire : surligne le prénom choisi et le retire.
Undo : réapparaît la dernière personne disparue.

Pas de scroll : les boutons de prénoms occupent tout l'espace disponible.
"""

import customtkinter as ctk

from session import Session

# ── Constantes de style ───────────────────────────────────────
_BG             = "#1a1a2e"
_BTN_DEFAULT    = "#2d2d44"
_BTN_HOVER      = "#3d3d5c"
_BTN_HIGHLIGHT  = "#1a5c2a"
_TXT_HIGHLIGHT  = "#4ADE80"
_TXT_NORMAL     = "#e0e0e0"
_TXT_COUNTER    = "#9CA3AF"
_BTN_ACTION     = "#374151"
_BTN_ACTION_HOV = "#4B5563"
_BTN_END        = "#7f1d1d"
_BTN_END_HOV    = "#DC2626"

# Célébration : texte jaune sur fond noir
_CELEBRATION_BG  = "#000000"
_CELEBRATION_TXT = "#FFD600"

# Hauteur réservée à la barre top + barre actions (en px)
_TOP_BAR_H    = 36
_ACTION_BAR_H = 44
_RESERVED_H   = _TOP_BAR_H + _ACTION_BAR_H + 20   # marges incluses


class SessionView(ctk.CTkFrame):
    """Vue principale pendant le déroulement du daily meeting."""

    VERTICAL   = "vertical"
    HORIZONTAL = "horizontal"

    def __init__(self, parent, on_end_session, get_window):
        super().__init__(parent, fg_color=_BG)
        self._session: Session | None = None
        self._on_end_session = on_end_session
        self._get_window = get_window
        self._layout = self.VERTICAL
        self._highlighted: str | None = None

        self._build_ui()

    # ── Construction UI ───────────────────────────────────────

    def _build_ui(self):
        # Barre supérieure : compteur + bouton layout
        top = ctk.CTkFrame(self, fg_color="transparent", height=_TOP_BAR_H)
        top.pack(fill="x", padx=6, pady=(4, 2))
        top.pack_propagate(False)

        self._counter_label = ctk.CTkLabel(
            top,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=_TXT_COUNTER,
            anchor="w",
        )
        self._counter_label.pack(side="left", fill="both", expand=True)

        self._layout_btn = ctk.CTkButton(
            top,
            text="⇄",
            width=28,
            height=22,
            font=ctk.CTkFont(size=13),
            fg_color=_BTN_ACTION,
            hover_color=_BTN_ACTION_HOV,
            command=self._toggle_layout,
        )
        self._layout_btn.pack(side="right", pady=4)

        # Zone des prénoms — frame simple (pas de scroll)
        # On utilise pack() avec fill+expand pour distribuer la hauteur dynamiquement
        self._names_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._names_outer.pack(fill="both", expand=True, padx=4, pady=2)
        # Recalcule les hauteurs de boutons à chaque redimensionnement de la zone
        self._names_outer.bind("<Configure>", self._on_names_resize)

        # Barre d'actions en bas (hauteur fixe)
        actions = ctk.CTkFrame(self, fg_color="transparent", height=_ACTION_BAR_H)
        actions.pack(fill="x", padx=6, pady=(2, 6))
        actions.pack_propagate(False)

        self._random_btn = ctk.CTkButton(
            actions,
            text="🎲",
            width=36,
            height=30,
            font=ctk.CTkFont(size=16),
            fg_color=_BTN_ACTION,
            hover_color="#1D4ED8",
            command=self._pick_random,
        )
        self._random_btn.pack(side="left", padx=(0, 4), pady=4)

        self._undo_btn = ctk.CTkButton(
            actions,
            text="↩",
            width=36,
            height=30,
            font=ctk.CTkFont(size=16),
            fg_color=_BTN_ACTION,
            hover_color=_BTN_ACTION_HOV,
            command=self._undo,
        )
        self._undo_btn.pack(side="left", padx=(0, 4), pady=4)

        self._end_btn = ctk.CTkButton(
            actions,
            text="■",
            width=36,
            height=30,
            font=ctk.CTkFont(size=14),
            fg_color=_BTN_END,
            hover_color=_BTN_END_HOV,
            command=self._on_end_session,
        )
        self._end_btn.pack(side="right", pady=4)

    def _on_names_resize(self, event):
        """Recalcule les hauteurs de boutons quand la zone change de taille."""
        if self._session is not None and not self._session.is_complete:
            self._refresh()

    # ── API publique ──────────────────────────────────────────

    def start_session(self, attendees: list[str]):
        """Démarre une nouvelle session avec les participants donnés."""
        self._session = Session(attendees)
        self._highlighted = None
        self._apply_layout()
        # Attendre que la fenêtre soit dessinée avant de calculer les hauteurs
        self._get_window().after(50, self._refresh)

    # ── Actions utilisateur ───────────────────────────────────

    def _mark_spoken(self, name: str):
        if self._session is None:
            return
        # Effacer le surlignage (quelle que soit la personne cliquée)
        self._highlighted = None
        self._session.mark_spoken(name)
        self._refresh()

    def _pick_random(self):
        """Tire au sort parmi les restants et surligne uniquement — ne marque pas."""
        if self._session is None or self._session.is_complete:
            return
        # Si quelqu'un est déjà surligné, on en tire un nouveau parmi les restants
        chosen = self._session.pick_random()
        if chosen:
            self._highlighted = chosen
            self._refresh()

    def _undo(self):
        if self._session is None:
            return
        # Si quelqu'un est surligné (tiré au sort mais pas encore cliqué),
        # on efface juste le surlignage sans toucher à la session
        if self._highlighted is not None:
            self._highlighted = None
            self._refresh()
            return
        # Sinon on annule le dernier clic (dernier spoken)
        restored = self._session.undo_last()
        if restored:
            self._refresh()

    # ── Layout ────────────────────────────────────────────────

    def _toggle_layout(self):
        if self._layout == self.VERTICAL:
            self._layout = self.HORIZONTAL
        else:
            self._layout = self.VERTICAL
        self._apply_layout()
        self._get_window().after(50, self._refresh)

    def _apply_layout(self):
        """Repositionne et redimensionne la fenêtre selon le layout."""
        win = self._get_window()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()

        if self._layout == self.VERTICAL:
            w = max(120, int(sw * 0.07))
            h = sh          # 100% de la hauteur
            x = sw - w
            y = 0
            win.geometry(f"{w}x{h}+{x}+{y}")
        else:               # HORIZONTAL
            w = sw
            h = 130
            x = 0
            y = 0
            win.geometry(f"{w}x{h}+{x}+{y}")

    # ── Rendu ─────────────────────────────────────────────────

    def _refresh(self):
        """Met à jour l'affichage, calcule la hauteur dynamique des boutons."""
        if self._session is None:
            return

        remaining  = self._session.remaining
        spoken_cnt = self._session.spoken_count
        total      = self._session.total

        # Compteur
        self._counter_label.configure(text=f"{spoken_cnt}/{total} ont parlé")

        # Vider la zone des prénoms
        for child in self._names_outer.winfo_children():
            child.destroy()

        # État boutons
        self._undo_btn.configure(state="normal" if spoken_cnt > 0 else "disabled")

        if self._session.is_complete:
            self._random_btn.configure(state="disabled")
            ctk.CTkLabel(
                self._names_outer,
                text="Tout le monde\na parlé !",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color=_TXT_HIGHLIGHT,
                justify="center",
            ).pack(expand=True)
            return

        self._random_btn.configure(state="normal")

        if self._layout == self.VERTICAL:
            self._render_vertical(remaining)
        else:
            self._render_horizontal(remaining)

    def _render_vertical(self, remaining: list[str]):
        """
        Affiche les prénoms en colonne.
        La hauteur de chaque bouton est calculée pour remplir tout l'espace
        disponible sans laisser de vide ni nécessiter de scroll.
        """
        n = len(remaining)
        if n == 0:
            return

        # Récupérer la hauteur réelle disponible dans _names_outer
        self.update_idletasks()
        available_h = self._names_outer.winfo_height()

        # Si la fenêtre n'est pas encore rendue, fallback
        if available_h < 10:
            available_h = self._get_window().winfo_height() - _RESERVED_H

        pad_total  = 4 * n          # pady=2 haut + bas par bouton
        btn_h      = max(24, (available_h - pad_total) // n)

        # Police adaptée à la taille du bouton (pas de plafond artificiel)
        font_size  = max(9, btn_h // 2)

        for name in remaining:
            is_hl = (name == self._highlighted)
            btn = ctk.CTkButton(
                self._names_outer,
                text=name,
                height=btn_h,
                font=ctk.CTkFont(
                    size=font_size,
                    weight="bold" if is_hl else "normal",
                ),
                fg_color=_BTN_HIGHLIGHT if is_hl else _BTN_DEFAULT,
                hover_color=_BTN_HOVER,
                text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                anchor="center",
                corner_radius=6,
                command=lambda nm=name: self._mark_spoken(nm),
            )
            btn.pack(fill="x", pady=2, padx=2)

    def _render_horizontal(self, remaining: list[str]):
        """
        Affiche les prénoms en ligne côte à côte.
        La largeur de chaque bouton est calculée pour remplir tout l'espace
        disponible sans scroll. La hauteur remplit la zone disponible.
        """
        n = len(remaining)
        if n == 0:
            return

        self.update_idletasks()
        available_w = self._names_outer.winfo_width()
        available_h = self._names_outer.winfo_height()

        if available_w < 10:
            available_w = self._get_window().winfo_width()
        if available_h < 10:
            available_h = self._get_window().winfo_height() - _RESERVED_H

        pad_total_w = 6 * n          # padx=3 gauche + droite par bouton
        btn_w = max(40, (available_w - pad_total_w) // n)

        pad_total_h = 6               # pady=3 haut + bas
        btn_h = max(24, available_h - pad_total_h)

        # Police adaptée à la taille du bouton (pas de plafond artificiel)
        font_size = max(9, btn_h // 2)

        wrap = ctk.CTkFrame(self._names_outer, fg_color="transparent")
        wrap.pack(fill="both", expand=True)

        for name in remaining:
            is_hl = (name == self._highlighted)
            btn = ctk.CTkButton(
                wrap,
                text=name,
                width=btn_w,
                height=btn_h,
                font=ctk.CTkFont(size=font_size, weight="bold" if is_hl else "normal"),
                fg_color=_BTN_HIGHLIGHT if is_hl else _BTN_DEFAULT,
                hover_color=_BTN_HOVER,
                text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                corner_radius=6,
                command=lambda nm=name: self._mark_spoken(nm),
            )
            btn.pack(side="left", padx=3, pady=3)
