# 03 — Vue Présence

La vue Présence (« Qui est présent ? ») sert à choisir les Participants avant de lancer une Session.

Sources Python : `ui/setup_view.py`, `ui/main_window.py`.

## Affichage

**PR-01** — La vue est reconstruite à partir de l'Équipe à chaque ouverture. Elle affiche donc toujours les derniers ajouts, suppressions, Icônes et Absents. (`ui/main_window.py:108`, `ui/setup_view.py:105-148`)

**PR-02** — Chaque Membre a une ligne, dans l'ordre de l'Équipe. Une ligne contient une case à cocher avec le nom du Membre, et son Icône (emoji ou image) si elle existe. (`ui/setup_view.py:125-146`)

**PR-03** `[CORRECTION]` — Une Icône image s'affiche en conservant ses proportions, dans un carré de 20 px `[INDICATIF]`.
Python : l'image était étirée en 20 × 20, ce qui la déformait. (`ui/setup_view.py:164`)

**PR-04** `[CHANGEMENT]` — Quand la vue s'ouvre, les Membres marqués Absents (`absent: true`) sont décochés. Tous les autres Membres sont cochés, y compris ceux qui n'ont jamais participé à une Session et ceux qui viennent d'être ajoutés.
Python : tous les Membres étaient cochés à chaque ouverture. (`ui/setup_view.py:127`)

**PR-05** — Un compteur affiche le nombre de cases cochées sur le nombre de Membres, par exemple `15/18 présent(s)` `[INDICATIF]`. Il se met à jour à chaque changement. (`ui/setup_view.py:180-183`)

## Actions

**PR-06** — Le bouton `Tout cocher` coche toutes les cases. Le bouton `Tout décocher` les décoche toutes. (`ui/setup_view.py:172-178`)

**PR-07** — Le bouton `<<< Retour` `[INDICATIF]` ramène à la vue Équipe, sans rien enregistrer. (`ui/setup_view.py:87-94`)

**PR-08** — Le bouton `Démarrer le Daily >>>` `[INDICATIF]` lance une Session. Les Membres cochés deviennent ses Participants, dans l'ordre de l'Équipe. Si aucune case n'est cochée, le bouton n'a aucun effet et aucun message ne s'affiche. (`ui/setup_view.py:185-194`)

**PR-09** `[CHANGEMENT]` — Au lancement d'une Session (PR-08 réussi), l'application enregistre les Absents :
- chaque Membre décoché est marqué Absent ;
- chaque Membre coché perd sa marque d'Absent ;
- l'Équipe est sauvegardée (voir PE-02).

Rien n'est enregistré dans les autres cas : retour à la vue Équipe, fermeture de l'application, clic sur `Démarrer` sans aucune case cochée.

**PR-10** — Si l'Équipe est vide, la vue affiche `Aucun membre dans l'équipe. Retournez en arrière pour en ajouter.` `[INDICATIF]` et le bouton `Démarrer` est désactivé. Ce cas ne peut pas se produire en passant par la vue Équipe (EQ-18), mais la vue doit quand même le gérer. (`ui/setup_view.py:114-121`)
