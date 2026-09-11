# 07 — Performance

La réécriture a pour but de supprimer les lenteurs de l'application Python. Les budgets ci-dessous sont des critères d'acceptation. Les règles de conception empêchent de reproduire les causes de lenteur de l'application Python.

## Budgets

Conditions de mesure : poste Windows 10 ou 11 standard, Équipe de 20 Membres ayant tous une Icône image, Session de 20 Participants.

| ID | Action | Budget | Lenteur constatée en Python |
|---|---|---|---|
| **PF-01** | Lancement de l'exe jusqu'à la vue Équipe affichée et utilisable | < 1 s | Démarrage lent |
| **PF-02** | Clic sur une Tuile jusqu'à l'affichage mis à jour | < 50 ms | Clic lent |
| **PF-03** | Passage de la fenêtre sur un écran de DPI différent | Aucun gel, nouvelle mise en page < 200 ms | Gel |
| **PF-04** | Clic sur ↔ jusqu'à la fenêtre recalée et les Tuiles affichées | < 100 ms | Calage lent |

**PF-05** — Les autres actions (ajout, suppression, fin d'un réordonnancement, changement d'Icône, Tirage, ouverture d'une vue) réagissent en moins de 100 ms. Le glisser-déposer suit la souris sans à-coups.

## Règles de conception

Chaque règle répond à une cause de lenteur trouvée dans le code Python.

**PF-10** — Une action ne reconstruit pas toute une liste. Elle met à jour seulement ce qui change : retirer une Tuile, mettre en évidence le Désigné, déplacer une ligne.
Python : toutes les Tuiles sont détruites puis recréées à chaque clic, Tirage ou annulation (`ui/session_view.py:407-429`), et toute la liste de la vue Équipe est reconstruite après chaque modification (`ui/team_view.py:159-180`).

**PF-11** — Une image n'est lue et décodée qu'une fois, jamais pendant l'affichage d'une Tuile ou d'une ligne.
Python : chaque image est relue sur le disque et redimensionnée à chaque affichage de chaque Tuile (`ui/session_view.py:708-728`). Le cache `_icon_cache` existe mais n'est pas utilisé à cet endroit (`ui/session_view.py:297-308`).

**PF-12** — La couleur dominante d'une image est calculée une fois, puis mise en cache.

**PF-13** — La taille des Tuiles découle de la mise en page (par exemple en CSS). Le code n'écoute pas les redimensionnements pour reconstruire l'interface, afin qu'aucune boucle de redimensionnement ne puisse se former.
Python : l'événement `<Configure>` déclenche une reconstruction complète, qui déclenche à son tour de nouveaux `<Configure>` (`ui/session_view.py:205-210`). C'est la cause du gel au changement d'écran et de la lenteur de ↔.

**PF-14** — Pendant un glisser-déposer, seules la ligne déplacée et l'indicateur d'insertion changent. Aucun élément n'est créé ni détruit à chaque mouvement de la souris.
Python : chaque mouvement recolore toutes les lignes et recrée l'indicateur (`ui/team_view.py:278-300`).

**PF-15** — Aucune attente fixe dans l'enchaînement des actions.
Python : le calage attend 150 ms avant d'afficher les Tuiles, puis ignore les redimensionnements pendant 300 ms supplémentaires (`ui/session_view.py:274-280`).

## Mesure

- PF-02 et PF-04 : un test Playwright mesure le temps entre l'action et l'affichage mis à jour. La recette manuelle confirme la mesure sur l'exe.
- PF-01 : en recette manuelle, on chronomètre le lancement de l'exe. Une version de développement journalise l'heure de lancement du processus et l'heure du premier affichage.
- PF-03 : en recette manuelle, avec deux écrans de DPI différents (par exemple 100 % et 150 %).
