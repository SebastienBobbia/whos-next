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

Nouvelles fonctionnalités :
  - Affichage de l'icône (emoji ou image) sur chaque tuile
  - Mode icône seule quand les tuiles sont trop petites
  - Couleur dominante de l'icône image appliquée en fond de tuile
"""

import customtkinter as ctk
from collections import Counter
from PIL import Image

from session import Session
from team_manager import TeamManager, Member
from ui.team_view import _open_image

# ── Constantes de style ───────────────────────────────────────
_BG = "#1a1a2e"
_BTN_DEFAULT = "#2d2d44"
_BTN_HOVER = "#3d3d5c"
_BTN_HIGHLIGHT = "#1a5c2a"
_TXT_HIGHLIGHT = "#4ADE80"
_TXT_NORMAL = "#e0e0e0"
_TXT_COUNTER = "#9CA3AF"
_BTN_ACTION = "#374151"
_BTN_ACTION_HOV = "#4B5563"
_BTN_END = "#7f1d1d"
_BTN_END_HOV = "#DC2626"

# Célébration : texte jaune sur fond noir
_CELEBRATION_BG = "#000000"
_CELEBRATION_TXT = "#FFD600"

# 4 boutons × 22px + 3 × 2px padding + 4px marges = ~98px minimum
_TOP_BAR_H = 26  # hauteur de la barre (bouton 22px + pady 2×2)
_RESERVED_H = _TOP_BAR_H + 10

# ── Seuils mode icône seule ───────────────────────────────────
# En dessous de ces dimensions la tuile n'affiche que l'icône
_ICON_ONLY_H = 48  # hauteur en vertical
_ICON_ONLY_W = 70  # largeur en horizontal


def _dominant_color(img: Image.Image, darken: float = 0.6) -> str:
    """
    Extrait la couleur dominante d'une image PIL et retourne un code hex CSS.
    La couleur est assombrie pour rester compatible avec le thème sombre.

    Les pixels transparents (alpha < 128) sont ignorés pour ne pas biaiser
    le résultat avec le fond des images PNG/RGBA.

    Args:
        img:     image PIL (RGB ou RGBA)
        darken:  facteur d'assombrissement [0..1], 1 = inchangée

    Returns:
        Couleur hex (#rrggbb) ou _BTN_DEFAULT si échec.
    """
    try:
        # S'assurer d'avoir du RGBA pour accéder au canal alpha
        rgba = img.convert("RGBA").resize((64, 64), Image.LANCZOS)

        # Extraire uniquement les pixels suffisamment opaques
        pixels_rgba = list(rgba.getdata())
        opaque = [(r, g, b) for r, g, b, a in pixels_rgba if a >= 128]

        if not opaque:
            return _BTN_DEFAULT

        # Construire une image RGB depuis les pixels opaques pour quantification
        rgb_img = Image.new("RGB", (len(opaque), 1))
        rgb_img.putdata(opaque)

        # Quantifier en N couleurs et prendre la plus fréquente
        quantized = rgb_img.quantize(colors=8, method=Image.Quantize.MEDIANCUT)
        palette = quantized.getpalette()  # flat list [r,g,b, r,g,b, ...]
        if not palette:
            return _BTN_DEFAULT

        counts = Counter(list(quantized.getdata()))
        dominant_idx = counts.most_common(1)[0][0]
        r = palette[dominant_idx * 3]
        g = palette[dominant_idx * 3 + 1]
        b = palette[dominant_idx * 3 + 2]

        # Assombrir la couleur pour le thème sombre
        r = int(r * darken)
        g = int(g * darken)
        b = int(b * darken)

        # Garantir que la couleur est suffisamment sombre (luminance < 140)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b
        if luminance > 140:
            r = int(r * 0.6)
            g = int(g * 0.6)
            b = int(b * 0.6)

        return f"#{r:02x}{g:02x}{b:02x}"
    except Exception:
        return _BTN_DEFAULT


class SessionView(ctk.CTkFrame):
    """Vue principale pendant le déroulement du daily meeting."""

    VERTICAL = "vertical"
    HORIZONTAL = "horizontal"

    def __init__(
        self,
        parent,
        on_end_session,
        get_window,
        team_manager: TeamManager | None = None,
    ):
        super().__init__(parent, fg_color=_BG)
        self._session: Session | None = None
        self._on_end_session = on_end_session
        self._get_window = get_window
        self._team: TeamManager | None = team_manager
        self._layout = self.VERTICAL
        self._highlighted: str | None = None

        # Cache : {name -> (CTkImage | None, dominant_color str)}
        self._icon_cache: dict[str, tuple] = {}

        self._build_ui()

    # ── Construction UI ───────────────────────────────────────

    def _build_ui(self):
        # Barre unique : boutons côte à côte, compacts
        self._top = ctk.CTkFrame(self, fg_color="transparent")
        self._top.pack(fill="x", padx=0, pady=(2, 1))

        # Zone des prénoms — prend tout l'espace restant
        self._names_outer = ctk.CTkFrame(self, fg_color="transparent")
        self._names_outer.pack(fill="both", expand=True, padx=2, pady=(0, 2))
        self._names_outer.bind("<Configure>", self._on_names_resize)

        btn_opts = dict(width=22, height=22, corner_radius=4, border_width=0)

        self._layout_btn = ctk.CTkButton(
            self._top,
            text="⇄",
            font=ctk.CTkFont(size=10),
            fg_color=_BTN_ACTION,
            hover_color=_BTN_ACTION_HOV,
            command=self._toggle_layout,
            **btn_opts,
        )
        self._random_btn = ctk.CTkButton(
            self._top,
            text="🎲",
            font=ctk.CTkFont(size=10),
            fg_color=_BTN_ACTION,
            hover_color="#1D4ED8",
            command=self._pick_random,
            **btn_opts,
        )
        self._undo_btn = ctk.CTkButton(
            self._top,
            text="↩",
            font=ctk.CTkFont(size=11),
            fg_color=_BTN_ACTION,
            hover_color=_BTN_ACTION_HOV,
            command=self._undo,
            **btn_opts,
        )
        self._end_btn = ctk.CTkButton(
            self._top,
            text="■",
            font=ctk.CTkFont(size=9),
            fg_color=_BTN_END,
            hover_color=_BTN_END_HOV,
            command=self._on_end_session,
            **btn_opts,
        )

        for btn in (self._layout_btn, self._random_btn, self._undo_btn, self._end_btn):
            btn.pack(side="left", padx=1, pady=1)

    def _place_buttons(self):
        pass  # layout fixe, rien à replacer

    def _on_names_resize(self, event):
        """Recalcule les hauteurs de boutons quand la zone change de taille."""
        if self._session is not None and not self._session.is_complete:
            self._refresh()

    # ── API publique ──────────────────────────────────────────

    def set_team_manager(self, team_manager: TeamManager):
        """Injecte le TeamManager (appelé depuis MainWindow)."""
        self._team = team_manager

    def start_session(self, attendees: list[str]):
        """Démarre une nouvelle session avec les participants donnés."""
        self._session = Session(attendees)
        self._highlighted = None
        # Précalculer le cache icônes pour les participants
        self._build_icon_cache(attendees)
        self._apply_layout()
        # Attendre que la fenêtre soit dessinée avant de calculer les hauteurs
        self._get_window().after(50, self._refresh)

    # ── Cache icônes ──────────────────────────────────────────

    def _build_icon_cache(self, names: list[str]):
        """Pré-charge les icônes de tous les participants."""
        self._icon_cache.clear()
        if self._team is None:
            return
        for name in names:
            member = self._team.get_member(name)
            if member is None:
                self._icon_cache[name] = (None, _BTN_DEFAULT)
                continue
            ctk_img, dom_color = self._load_member_icon(member)
            self._icon_cache[name] = (ctk_img, dom_color)

    def _load_member_icon(self, member: Member, size: int = 32) -> tuple:
        """
        Charge l'icône d'un membre et extrait sa couleur dominante.

        Returns:
            (CTkImage | None, dominant_color str)
        """
        if member["icon_type"] == "image":
            img_path = self._team.get_icon_path(member)
            if img_path:
                try:
                    pil_img = _open_image(img_path)
                    dom = _dominant_color(pil_img)
                    # Redimensionner en conservant les proportions (fit dans size×size)
                    pil_img.thumbnail((size, size), Image.LANCZOS)
                    ctk_img = ctk.CTkImage(pil_img, size=pil_img.size)
                    return ctk_img, dom
                except Exception:
                    pass
        # Emoji ou pas d'icône : pas d'image CTk, pas de couleur dominante
        return None, _BTN_DEFAULT

    def _get_icon_info(self, name: str) -> tuple:
        """
        Retourne (CTkImage | None, emoji_str | None, dominant_color) pour un nom.
        """
        ctk_img, dom_color = self._icon_cache.get(name, (None, _BTN_DEFAULT))
        emoji = None
        if self._team:
            member = self._team.get_member(name)
            if member and member["icon_type"] == "emoji" and member["icon_value"]:
                emoji = member["icon_value"]
        return ctk_img, emoji, dom_color

    # ── Actions utilisateur ───────────────────────────────────

    def _mark_spoken(self, name: str):
        if self._session is None:
            return
        self._highlighted = None
        self._session.mark_spoken(name)
        self._refresh()

    def _pick_random(self):
        """Tire au sort parmi les restants et surligne uniquement — ne marque pas."""
        if self._session is None or self._session.is_complete:
            return
        chosen = self._session.pick_random()
        if chosen:
            self._highlighted = chosen
            self._refresh()

    def _undo(self):
        if self._session is None:
            return
        if self._highlighted is not None:
            self._highlighted = None
            self._refresh()
            return
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
            w = max(98, int(sw * 0.07))
            h = sh
            x = sw - w
            y = 0
            win.geometry(f"{w}x{h}+{x}+{y}")
        else:  # HORIZONTAL
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

        remaining = self._session.remaining
        spoken_cnt = self._session.spoken_count

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
        puis ferme automatiquement l'application après ~1 seconde.
        """
        win = self._get_window()

        self.configure(fg_color=_CELEBRATION_BG)
        self._names_outer.configure(fg_color=_CELEBRATION_BG)

        self.update_idletasks()
        available_w = self._names_outer.winfo_width()
        available_h = self._names_outer.winfo_height()
        if available_w < 10:
            available_w = win.winfo_width()
        if available_h < 10:
            available_h = win.winfo_height() - _RESERVED_H

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

        _colors = [_CELEBRATION_TXT, "#997F00"]
        _state = {"step": 0, "running": True}

        def _pulse():
            if not _state["running"]:
                return
            color = _colors[_state["step"] % 2]
            label.configure(text_color=color)
            _state["step"] += 1
            win.after(250, _pulse)

        _pulse()

        def _close():
            _state["running"] = False
            self._get_window().destroy()

        win.after(1000, _close)

    # ── Rendu vertical ────────────────────────────────────────

    def _render_vertical(self, remaining: list[str]):
        """
        Affiche les prénoms en colonne.
        Bascule en mode icône seule si la tuile est trop petite.
        """
        n = len(remaining)
        if n == 0:
            return

        self.update_idletasks()
        available_h = self._names_outer.winfo_height()
        if available_h < 10:
            available_h = self._get_window().winfo_height() - _RESERVED_H

        available_w = self._names_outer.winfo_width()
        if available_w < 10:
            available_w = self._get_window().winfo_width()

        pad_total = 4 * n
        btn_h = max(24, (available_h - pad_total) // n)
        font_size = max(9, min(btn_h // 2, available_w // 6))

        # Mode icône seule si tuile trop petite
        icon_only = btn_h < _ICON_ONLY_H

        for name in remaining:
            is_hl = name == self._highlighted
            ctk_img, emoji, dom_color = self._get_icon_info(name)

            # Couleur de fond : highlight > couleur dominante > défaut
            if is_hl:
                fg = _BTN_HIGHLIGHT
            elif dom_color != _BTN_DEFAULT:
                fg = dom_color
            else:
                fg = _BTN_DEFAULT

            # Préparer l'image redimensionnée selon la hauteur de tuile
            img_for_btn = None
            if not icon_only and ctk_img is not None:
                icon_sz = max(16, min(btn_h - 16, 40))
                img_for_btn = self._resize_ctk_image(name, icon_sz)

            if icon_only:
                # Mode compact : icône seule (emoji ou image)
                self._render_tile_icon_only(
                    name, btn_h, available_w, ctk_img, emoji, fg, is_hl
                )
            elif img_for_btn is not None:
                # Image + texte
                self._render_tile_image_text_vertical(
                    name, btn_h, available_w, font_size, img_for_btn, fg, is_hl
                )
            elif emoji:
                # Emoji + texte
                self._render_tile_emoji_text_vertical(
                    name, btn_h, available_w, font_size, emoji, fg, is_hl
                )
            else:
                # Texte seul (pas d'icône)
                btn = ctk.CTkButton(
                    self._names_outer,
                    text=name,
                    height=btn_h,
                    font=ctk.CTkFont(
                        size=font_size,
                        weight="bold" if is_hl else "normal",
                    ),
                    fg_color=fg,
                    hover_color=_BTN_HOVER,
                    text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                    anchor="center",
                    corner_radius=6,
                    command=lambda nm=name: self._mark_spoken(nm),
                )
                btn.pack(fill="x", pady=2, padx=2)

    def _render_tile_icon_only(
        self, name, btn_h, available_w, ctk_img, emoji, fg, is_hl
    ):
        """Tuile en mode icône seule (compact)."""
        icon_sz = max(12, btn_h - 8)
        img = self._resize_ctk_image(name, icon_sz) if ctk_img is not None else None

        if img is not None:
            btn = ctk.CTkButton(
                self._names_outer,
                text="",
                image=img,
                height=btn_h,
                fg_color=_BTN_HIGHLIGHT if is_hl else fg,
                hover_color=_BTN_HOVER,
                corner_radius=6,
                command=lambda nm=name: self._mark_spoken(nm),
            )
        elif emoji:
            font_sz = max(9, min(btn_h - 8, available_w - 4))
            btn = ctk.CTkButton(
                self._names_outer,
                text=emoji,
                height=btn_h,
                font=ctk.CTkFont(size=font_sz),
                fg_color=_BTN_HIGHLIGHT if is_hl else fg,
                hover_color=_BTN_HOVER,
                text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                corner_radius=6,
                command=lambda nm=name: self._mark_spoken(nm),
            )
        else:
            # Pas d'icône : initiales
            initials = name[0].upper() if name else "?"
            font_sz = max(9, min(btn_h - 8, available_w - 4))
            btn = ctk.CTkButton(
                self._names_outer,
                text=initials,
                height=btn_h,
                font=ctk.CTkFont(size=font_sz, weight="bold"),
                fg_color=_BTN_HIGHLIGHT if is_hl else fg,
                hover_color=_BTN_HOVER,
                text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                corner_radius=6,
                command=lambda nm=name: self._mark_spoken(nm),
            )
        btn.pack(fill="x", pady=2, padx=2)

    def _render_tile_image_text_vertical(
        self, name, btn_h, available_w, font_size, img, fg, is_hl
    ):
        """Tuile image + texte en mode vertical."""
        btn = ctk.CTkButton(
            self._names_outer,
            text=name,
            image=img,
            compound="left",
            height=btn_h,
            font=ctk.CTkFont(
                size=font_size,
                weight="bold" if is_hl else "normal",
            ),
            fg_color=_BTN_HIGHLIGHT if is_hl else fg,
            hover_color=_BTN_HOVER,
            text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
            anchor="center",
            corner_radius=6,
            command=lambda nm=name: self._mark_spoken(nm),
        )
        btn.pack(fill="x", pady=2, padx=2)

    def _render_tile_emoji_text_vertical(
        self, name, btn_h, available_w, font_size, emoji, fg, is_hl
    ):
        """Tuile emoji + texte : emoji dans un label + bouton texte côte à côte."""
        wrapper = ctk.CTkFrame(
            self._names_outer,
            height=btn_h,
            fg_color=_BTN_HIGHLIGHT if is_hl else fg,
            corner_radius=6,
        )
        wrapper.pack(fill="x", pady=2, padx=2)
        wrapper.pack_propagate(False)

        emoji_lbl = ctk.CTkLabel(
            wrapper,
            text=emoji,
            font=ctk.CTkFont(size=max(10, font_size)),
            fg_color="transparent",
            width=font_size + 8,
        )
        emoji_lbl.pack(side="left", padx=(6, 0))

        name_lbl = ctk.CTkLabel(
            wrapper,
            text=name,
            font=ctk.CTkFont(
                size=font_size,
                weight="bold" if is_hl else "normal",
            ),
            fg_color="transparent",
            text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
            anchor="center",
        )
        name_lbl.pack(side="left", fill="both", expand=True)

        # Rendre toute la tuile cliquable
        for w in (wrapper, emoji_lbl, name_lbl):
            w.bind("<Button-1>", lambda e, nm=name: self._mark_spoken(nm))
            w.configure(cursor="hand2")

    # ── Rendu horizontal ──────────────────────────────────────

    def _render_horizontal(self, remaining: list[str]):
        """
        Affiche les prénoms en ligne côte à côte.
        Bascule en mode icône seule si la tuile est trop étroite.
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

        pad_total_w = 6 * n
        btn_w = max(40, (available_w - pad_total_w) // n)

        pad_total_h = 6
        btn_h = max(24, available_h - pad_total_h)

        font_size = max(9, btn_h // 2)

        # Mode icône seule si tuile trop étroite
        icon_only = btn_w < _ICON_ONLY_W

        wrap = ctk.CTkFrame(self._names_outer, fg_color="transparent")
        wrap.pack(fill="both", expand=True)

        for name in remaining:
            is_hl = name == self._highlighted
            ctk_img, emoji, dom_color = self._get_icon_info(name)

            if is_hl:
                fg = _BTN_HIGHLIGHT
            elif dom_color != _BTN_DEFAULT:
                fg = dom_color
            else:
                fg = _BTN_DEFAULT

            if icon_only:
                self._render_h_tile_icon_only(
                    wrap, name, btn_w, btn_h, ctk_img, emoji, fg, is_hl
                )
            elif ctk_img is not None:
                icon_sz = max(16, min(btn_h - 16, 40))
                img = self._resize_ctk_image(name, icon_sz)
                btn = ctk.CTkButton(
                    wrap,
                    text=name,
                    image=img,
                    compound="top",
                    width=btn_w,
                    height=btn_h,
                    font=ctk.CTkFont(
                        size=font_size, weight="bold" if is_hl else "normal"
                    ),
                    fg_color=fg,
                    hover_color=_BTN_HOVER,
                    text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                    corner_radius=6,
                    command=lambda nm=name: self._mark_spoken(nm),
                )
                btn.pack(side="left", padx=3, pady=3)
            elif emoji:
                # Frame wrapper avec emoji au-dessus du nom
                wrapper = ctk.CTkFrame(
                    wrap,
                    width=btn_w,
                    height=btn_h,
                    fg_color=fg,
                    corner_radius=6,
                )
                wrapper.pack(side="left", padx=3, pady=3)
                wrapper.pack_propagate(False)

                ctk.CTkLabel(
                    wrapper,
                    text=emoji,
                    font=ctk.CTkFont(size=max(10, font_size)),
                    fg_color="transparent",
                ).pack(expand=True)

                ctk.CTkLabel(
                    wrapper,
                    text=name,
                    font=ctk.CTkFont(
                        size=max(8, font_size - 2), weight="bold" if is_hl else "normal"
                    ),
                    fg_color="transparent",
                    text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                ).pack()

                for w in wrapper.winfo_children() + [wrapper]:
                    w.bind("<Button-1>", lambda e, nm=name: self._mark_spoken(nm))
                    w.configure(cursor="hand2")
            else:
                btn = ctk.CTkButton(
                    wrap,
                    text=name,
                    width=btn_w,
                    height=btn_h,
                    font=ctk.CTkFont(
                        size=font_size, weight="bold" if is_hl else "normal"
                    ),
                    fg_color=fg,
                    hover_color=_BTN_HOVER,
                    text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                    corner_radius=6,
                    command=lambda nm=name: self._mark_spoken(nm),
                )
                btn.pack(side="left", padx=3, pady=3)

    def _render_h_tile_icon_only(
        self, parent, name, btn_w, btn_h, ctk_img, emoji, fg, is_hl
    ):
        """Tuile en mode icône seule (horizontal compact)."""
        icon_sz = max(12, min(btn_h - 8, btn_w - 8))
        img = self._resize_ctk_image(name, icon_sz) if ctk_img is not None else None

        if img is not None:
            btn = ctk.CTkButton(
                parent,
                text="",
                image=img,
                width=btn_w,
                height=btn_h,
                fg_color=_BTN_HIGHLIGHT if is_hl else fg,
                hover_color=_BTN_HOVER,
                corner_radius=6,
                command=lambda nm=name: self._mark_spoken(nm),
            )
        elif emoji:
            font_sz = max(9, min(btn_h - 8, btn_w - 4))
            btn = ctk.CTkButton(
                parent,
                text=emoji,
                width=btn_w,
                height=btn_h,
                font=ctk.CTkFont(size=font_sz),
                fg_color=_BTN_HIGHLIGHT if is_hl else fg,
                hover_color=_BTN_HOVER,
                text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                corner_radius=6,
                command=lambda nm=name: self._mark_spoken(nm),
            )
        else:
            initials = name[0].upper() if name else "?"
            font_sz = max(9, min(btn_h - 8, btn_w - 4))
            btn = ctk.CTkButton(
                parent,
                text=initials,
                width=btn_w,
                height=btn_h,
                font=ctk.CTkFont(size=font_sz, weight="bold"),
                fg_color=_BTN_HIGHLIGHT if is_hl else fg,
                hover_color=_BTN_HOVER,
                text_color=_TXT_HIGHLIGHT if is_hl else _TXT_NORMAL,
                corner_radius=6,
                command=lambda nm=name: self._mark_spoken(nm),
            )
        btn.pack(side="left", padx=3, pady=3)

    # ── Cache images redimensionnées ──────────────────────────

    def _resize_ctk_image(self, name: str, size: int) -> ctk.CTkImage | None:
        """
        Retourne une CTkImage redimensionnée à `size`×`size` pour ce membre.
        Utilise le cache et recharge depuis le TeamManager si nécessaire.
        Le redimensionnement conserve les proportions (fit, pas de crop).
        """
        if self._team is None:
            return None
        member = self._team.get_member(name)
        if member is None or member["icon_type"] != "image":
            return None
        img_path = self._team.get_icon_path(member)
        if img_path is None:
            return None
        try:
            pil_img = _open_image(img_path)
            # Redimensionner en conservant les proportions (fit dans size×size)
            pil_img.thumbnail((size, size), Image.LANCZOS)
            return ctk.CTkImage(pil_img, size=pil_img.size)
        except Exception:
            return None
