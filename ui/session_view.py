"""
SessionView — Vue live du daily meeting.

Design compact, deux modes :
  - VERTICAL   : fenêtre collée au bord droit, largeur 7% écran
  - HORIZONTAL : fenêtre collée au bord haut, pleine largeur

Seuls les participants qui n'ont pas encore parlé sont affichés.
Cliquer sur un nom le fait disparaître (= a parlé).
Tirage aléatoire : surligne le prénom choisi et le retire.
Undo : réapparaît la dernière personne disparue.
"""

import customtkinter as ctk

from session import Session

# ── Constantes de style ───────────────────────────────────────
_BG             = "#1a1a2e"      # fond global
_BTN_DEFAULT    = "#2d2d44"      # bouton prénom normal
_BTN_HOVER      = "#3d3d5c"      # survol
_BTN_HIGHLIGHT  = "#1a5c2a"      # surligné après tirage (fond)
_TXT_HIGHLIGHT  = "#4ADE80"      # texte surligné
_TXT_NORMAL     = "#e0e0e0"      # texte normal
_TXT_COUNTER    = "#9CA3AF"      # compteur grisé
_BTN_ACTION     = "#374151"      # boutons d'action
_BTN_ACTION_HOV = "#4B5563"
_BTN_END        = "#7f1d1d"
_BTN_END_HOV    = "#DC2626"


class SessionView(ctk.CTkFrame):
    """Vue principale pendant le déroulement du daily meeting."""

    VERTICAL   = "vertical"
    HORIZONTAL = "horizontal"

    def __init__(self, parent, on_end_session, get_window):
        """
        Args:
            parent        : widget parent
            on_end_session: callback appelé quand l'utilisateur termine le daily
            get_window    : callable retournant la CTk root (pour repositionner)
        """
        super().__init__(parent, fg_color=_BG)
        self._session: Session | None = None
        self._on_end_session = on_end_session
        self._get_window = get_window
        self._layout = self.VERTICAL
        self._highlighted: str | None = None   # dernier tiré au sort (surligné)

        self._build_ui()

    # ── Construction UI ───────────────────────────────────────

    def _build_ui(self):
        # Barre supérieure : compteur + bouton layout
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", padx=6, pady=(6, 2))

        self._counter_label = ctk.CTkLabel(
            top,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=_TXT_COUNTER,
            anchor="w",
        )
        self._counter_label.pack(side="left", fill="x", expand=True)

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
        self._layout_btn.pack(side="right")

        # Zone des prénoms (scrollable, s'adapte au layout)
        self._names_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._names_outer.pack(fill="both", expand=True, padx=4, pady=2)

        # Conteneur scrollable des prénoms
        self._names_scroll = ctk.CTkScrollableFrame(
            self._names_outer, fg_color="transparent", scrollbar_button_color=_BTN_ACTION
        )
        self._names_scroll.pack(fill="both", expand=True)

        # Barre d'actions en bas
        actions = ctk.CTkFrame(self, fg_color="transparent")
        actions.pack(fill="x", padx=6, pady=(2, 6))

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
        self._random_btn.pack(side="left", padx=(0, 4))

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
        self._undo_btn.pack(side="left", padx=(0, 4))

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
        self._end_btn.pack(side="right")

    # ── API publique ──────────────────────────────────────────

    def start_session(self, attendees: list[str]):
        """Démarre une nouvelle session avec les participants donnés."""
        self._session = Session(attendees)
        self._highlighted = None
        self._apply_layout()
        self._refresh()

    # ── Actions utilisateur ───────────────────────────────────

    def _mark_spoken(self, name: str):
        """Clic sur un prénom → il a parlé, disparaît."""
        if self._session is None:
            return
        if self._highlighted == name:
            self._highlighted = None
        self._session.mark_spoken(name)
        self._refresh()

    def _pick_random(self):
        """Tire au sort parmi les restants, surligne + retire."""
        if self._session is None or self._session.is_complete:
            return
        chosen = self._session.pick_random()
        if chosen:
            self._highlighted = chosen
            self._refresh()

    def _undo(self):
        """Annule le dernier événement : réapparaît le dernier nom disparu."""
        if self._session is None:
            return
        restored = self._session.undo_last()
        if restored:
            # Si le nom restauré était le surligné, on efface le surlignage
            if self._highlighted == restored:
                self._highlighted = None
            self._refresh()

    # ── Layout ────────────────────────────────────────────────

    def _toggle_layout(self):
        """Bascule entre mode vertical et horizontal."""
        if self._layout == self.VERTICAL:
            self._layout = self.HORIZONTAL
        else:
            self._layout = self.VERTICAL
        self._apply_layout()
        self._refresh()

    def _apply_layout(self):
        """Repositionne et redimensionne la fenêtre selon le layout."""
        win = self._get_window()
        sw = win.winfo_screenwidth()
        sh = win.winfo_screenheight()

        if self._layout == self.VERTICAL:
            w = max(120, int(sw * 0.07))
            h = int(sh * 0.80)
            x = sw - w
            y = int(sh * 0.10)
            win.geometry(f"{w}x{h}+{x}+{y}")

            # Réorganiser le scroll en vertical
            self._names_scroll.configure(orientation="vertical")   # type: ignore[call-arg]

        else:  # HORIZONTAL
            w = sw
            h = 130
            x = 0
            y = 0
            win.geometry(f"{w}x{h}+{x}+{y}")

    # ── Rendu ─────────────────────────────────────────────────

    def _refresh(self):
        """Met à jour l'affichage."""
        if self._session is None:
            return

        remaining = self._session.remaining
        spoken_count = self._session.spoken_count
        total = self._session.total

        # Compteur
        self._counter_label.configure(text=f"{spoken_count}/{total} ont parlé")

        # Vider la zone des prénoms
        for w in self._names_scroll.winfo_children():
            w.destroy()

        if self._session.is_complete:
            ctk.CTkLabel(
                self._names_scroll,
                text="Tout le monde\na parlé !",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=_TXT_HIGHLIGHT,
                justify="center",
            ).pack(pady=10, padx=4)
            self._random_btn.configure(state="disabled")
            return

        self._random_btn.configure(state="normal")

        if self._layout == self.VERTICAL:
            self._render_vertical(remaining)
        else:
            self._render_horizontal(remaining)

        # Undo disponible seulement si quelqu'un a parlé
        self._undo_btn.configure(
            state="normal" if spoken_count > 0 else "disabled"
        )

    def _render_vertical(self, remaining: list[str]):
        """Affiche les prénoms en colonne."""
        for name in remaining:
            is_hl = (name == self._highlighted)
            btn = ctk.CTkButton(
                self._names_scroll,
                text=name,
                height=32,
                font=ctk.CTkFont(size=13, weight="bold" if is_hl else "normal"),
                fg_color=_BTN_HIGHLIGHT if is_hl else _BTN_DEFAULT,
                hover_color=_BTN_HOVER,
                text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                anchor="center",
                corner_radius=6,
                command=lambda n=name: self._mark_spoken(n),
            )
            btn.pack(fill="x", pady=2, padx=2)

    def _render_horizontal(self, remaining: list[str]):
        """Affiche les prénoms en ligne (wrap manuel par frame)."""
        # On utilise un frame avec wrapping via pack en mode left
        wrap_frame = ctk.CTkFrame(self._names_scroll, fg_color="transparent")
        wrap_frame.pack(fill="both", expand=True)

        for name in remaining:
            is_hl = (name == self._highlighted)
            btn = ctk.CTkButton(
                wrap_frame,
                text=name,
                height=30,
                font=ctk.CTkFont(size=12, weight="bold" if is_hl else "normal"),
                fg_color=_BTN_HIGHLIGHT if is_hl else _BTN_DEFAULT,
                hover_color=_BTN_HOVER,
                text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                corner_radius=6,
                command=lambda n=name: self._mark_spoken(n),
            )
            btn.pack(side="left", padx=3, pady=3)
