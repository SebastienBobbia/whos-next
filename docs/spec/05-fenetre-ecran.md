# 05 — Fenêtre et écran

Ce fichier décrit la fenêtre principale, l'option « toujours au premier plan », le calage de la fenêtre au bord droit de l'écran en Session, et le comportement avec plusieurs écrans de DPI différents.

Sources Python : `ui/main_window.py`, `ui/session_view.py`, `ui/dpi_utils.py`.

## Fenêtre

**FE-01** — L'application a une seule fenêtre principale, titrée `Who's Next?`, avec le logo de l'application comme icône (`assets/logo.ico`). La fenêtre de choix d'Icône et le sélecteur de fichiers sont les seules fenêtres secondaires. (`ui/main_window.py:27-35`)

**FE-02** — L'application utilise uniquement un thème sombre.

**FE-03** — Chaque fois que la vue Équipe ou la vue Présence s'affiche, la fenêtre reprend la taille 420 × 550 px `[INDICATIF]`. Sa position ne change pas. Elle reste redimensionnable, avec une taille minimale de 350 × 450 px `[INDICATIF]`. (`ui/main_window.py:92-109`)

**FE-04** — Fermer la fenêtre termine l'application, sans confirmation. Une Session en cours est perdue.

## Premier plan

**FE-05** — La fenêtre est toujours au premier plan dès le lancement. Une case `Toujours au premier plan` `[INDICATIF]`, en bas des vues Équipe et Présence, active ou désactive ce mode immédiatement. (`ui/main_window.py:30`, `:67-79`, `:136-138`)

**FE-06** — La case est masquée pendant la Session, mais son état reste appliqué. Cet état se conserve tant que l'application tourne, y compris d'une Session à l'autre. Il n'est jamais sauvegardé : au lancement suivant, le mode est de nouveau activé. (`ui/main_window.py:95`, `:105`, `:115`)

## Calage en Session

**FE-07** — Le calage a lieu au démarrage de chaque Session et à chaque clic sur ↔. Il place la fenêtre ainsi : (`ui/session_view.py:229-280`)
- l'écran de référence est celui qui contient la fenêtre, ou le plus proche d'elle ;
- la zone de travail de cet écran exclut la barre des tâches ;
- la fenêtre occupe toute la hauteur de la zone de travail ;
- son bord droit touche le bord droit de la zone de travail, et son bord supérieur touche le haut de la zone de travail ;
- sa largeur est celle du plus long nom parmi les Restants, plus la place d'une Icône et des marges. Dans l'application Python `[INDICATIF]` : texte mesuré en Segoe UI 14 gras, + 36 px pour l'Icône, + 28 px de marges ;
- la largeur ne dépasse pas 18 % de la largeur de la zone de travail, et ne descend pas sous un minimum (90 px dans l'application Python `[INDICATIF]`).

**FE-08** `[CORRECTION]` (sous réserve de PT-4) — Après un calage, la fenêtre entière (cadre et barre de titre compris, s'il y en a) tient dans la zone de travail.

**FE-09** — La largeur ne change qu'au calage. Quand un Participant au nom long A parlé, la fenêtre ne rétrécit qu'au prochain clic sur ↔. (`ui/session_view.py:255-263`)

**FE-10** — Quand la Session se termine par le bouton de fin, l'application revient à la vue Équipe : la fenêtre reprend la taille de FE-03, sans changer de position, et la case `Toujours au premier plan` réapparaît. (`ui/main_window.py:121-123`)

**FE-11** — Pendant la Session, la taille minimale de la fenêtre est de 120 × 100 px `[INDICATIF]`. On peut redimensionner la fenêtre à la main, et les Tuiles s'adaptent (SE-16). (`ui/main_window.py:117`)

## DPI et multi-écran

**FE-12** — Toutes les tailles de cette spécification sont en pixels logiques (96 DPI = 100 %). Sur un écran à 150 %, une Tuile de 48 px logiques mesure 72 px physiques.

**FE-13** — Quand on déplace la fenêtre sur un écran de DPI différent, l'interface garde sa taille logique : elle est mise à l'échelle du nouvel écran. La fenêtre ne se recale pas toute seule, ni en position ni en hauteur. Le calage sur le nouvel écran se fait par un clic sur ↔. Ce passage d'un écran à l'autre ne doit provoquer aucun gel (voir PF-03).

**FE-14** — Avec plusieurs écrans, ↔ utilise toujours l'écran où se trouve la fenêtre au moment du clic, avec la zone de travail et le DPI de cet écran. (`ui/dpi_utils.py:47-80`)
