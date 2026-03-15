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

# Hauteur réservée aux boutons en mode vertical (4 × (24+2px pady) + marges)
_TOP_BAR_H  = 4 * 26 + 10   # ~114px
_RESERVED_H = _TOP_BAR_H + 10


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
        # Conteneur de la barre de boutons (reconstruit selon layout)
        self._top = ctk.CTkFrame(self, fg_color="transparent")
        self._top.pack(fill="x", padx=2, pady=(2, 1))

        # Zone des prénoms — prend tout l'espace restant
        self._names_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._names_outer.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        self._names_outer.bind("<Configure>", self._on_names_resize)

        # Créer les boutons (sans les placer encore)
        self._layout_btn = ctk.CTkButton(
            self._top, text="⇄", width=26, height=24,
            font=ctk.CTkFont(size=11),
            fg_color=_BTN_ACTION, hover_color=_BTN_ACTION_HOV,
            command=self._toggle_layout,
        )
        self._random_btn = ctk.CTkButton(
            self._top, text="🎲", width=26, height=24,
            font=ctk.CTkFont(size=12),
            fg_color=_BTN_ACTION, hover_color="#1D4ED8",
            command=self._pick_random,
        )
        self._undo_btn = ctk.CTkButton(
            self._top, text="↩", width=26, height=24,
            font=ctk.CTkFont(size=12),
            fg_color=_BTN_ACTION, hover_color=_BTN_ACTION_HOV,
            command=self._undo,
        )
        self._end_btn = ctk.CTkButton(
            self._top, text="■", width=26, height=24,
            font=ctk.CTkFont(size=11),
            fg_color=_BTN_END, hover_color=_BTN_END_HOV,
            command=self._on_end_session,
        )

    def _place_buttons(self):
        """Replace les boutons selon le layout courant."""
        for btn in (self._layout_btn, self._random_btn,
                    self._undo_btn, self._end_btn):
            btn.pack_forget()

        if self._layout == self.VERTICAL:
            # En vertical : fenêtre étroite → boutons empilés verticalement
            for btn in (self._layout_btn, self._random_btn,
                        self._undo_btn, self._end_btn):
                btn.pack(fill="x", padx=2, pady=1)
        else:
            # En horizontal : place suffisante → boutons sur une ligne
            for btn in (self._layout_btn, self._random_btn,
                        self._undo_btn, self._end_btn):
                btn.pack(side="left", padx=2, pady=2)

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
            w = max(34, int(sw * 0.07))   # 34px = largeur bouton + paddings
            h = sh
            x = sw - w
            y = 0
            win.geometry(f"{w}x{h}+{x}+{y}")
        else:               # HORIZONTAL
            w = sw
            h = max(60, int(sh * 0.05))
            x = 0
            y = 0
            win.geometry(f"{w}x{h}+{x}+{y}")

        self._place_buttons()

    # ── Rendu ─────────────────────────────────────────────────

    def _refresh(self):
        """Met à jour l'affichage, calcule la hauteur dynamique des boutons."""
        if self._session is None:
            return

        remaining  = self._session.remaining
        spoken_cnt = self._session.spoken_count
        total      = self._session.total

        # Compteur (supprimé de l'affichage — on garde juste le titre)
        pass

        # Vider la zone des prénoms
        for child in self._names_outer.winfo_children():
            child.destroy()

        # État boutons
        self._undo_btn.configure(state="normal" if spoken_cnt > 0 else "disabled")

        if self._session.is_complete:
            self._random_btn.configure(state="disabled")
            self._undo_btn.configure(state="disabled")
            self._show_celebration()
            return

        self._random_btn.configure(state="normal")

        if self._layout == self.VERTICAL:
            self._render_vertical(remaining)
        else:
            self._render_horizontal(remaining)

    def _show_celebration(self):
        """
        Affiche une animation de célébration (texte jaune sur fond noir)
        puis ferme automatiquement l'application après ~3 secondes.
        """
        win = self._get_window()

        # Fond noir sur toute la fenêtre
        self.configure(fg_color=_CELEBRATION_BG)
        self._names_outer.configure(fg_color=_CELEBRATION_BG)

        # Taille de police dynamique selon la zone disponible
        self.update_idletasks()
        available_w = self._names_outer.winfo_width()
        available_h = self._names_outer.winfo_height()
        if available_w < 10:
            available_w = win.winfo_width()
        if available_h < 10:
            available_h = win.winfo_height() - _RESERVED_H

        # Le texte fait ~16 caractères sur 2 lignes — on borne la police
        # pour qu'elle rentre dans la largeur ET la hauteur disponibles
        font_size = max(10, min(available_h // 4, available_w // 9))

        label = ctk.CTkLabel(
            self._names_outer,
            text="Tout le monde\na parlé ! 🎉",
            font=ctk.CTkFont(size=font_size, weight="bold"),
            text_color=_CELEBRATION_TXT,
            fg_color=_CELEBRATION_BG,
            justify="center",
        )
        label.pack(expand=True)

        # Animation de pulse : alterne entre jaune vif et jaune foncé
        _colors = [_CELEBRATION_TXT, "#997F00"]
        _state  = {"step": 0, "running": True}

        def _pulse():
            if not _state["running"]:
                return
            color = _colors[_state["step"] % 2]
            label.configure(text_color=color)
            _state["step"] += 1
            win.after(250, _pulse)

        _pulse()

        # Auto-fermeture complète de l'application après 1 seconde
        def _close():
            _state["running"] = False
            self._get_window().destroy()

        win.after(1000, _close)

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

        # Largeur réelle disponible pour les boutons
        self.update_idletasks()
        available_w = self._names_outer.winfo_width()
        if available_w < 10:
            available_w = self._get_window().winfo_width()

        # Police : limitée par la hauteur ET la largeur du bouton
        font_size  = max(9, min(btn_h // 2, available_w // 6))

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
