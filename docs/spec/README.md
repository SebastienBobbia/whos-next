# Spécification fonctionnelle — Who's Next?

Cette spécification décrit ce que doit faire la réécriture Tauri 2 (voir [ADR 0001](../adr/0001-reecriture-tauri-2.md)). Elle a été construite en lisant le code Python de l'application actuelle. Le README du dépôt n'est pas à jour : il ne sert pas de référence. Le vocabulaire (Membre, Participant, Désigné…) est défini dans [CONTEXT.md](../../CONTEXT.md).

## Règle de base

Le comportement du code Python actuel fait foi. Il existe trois exceptions, chacune signalée par une étiquette :

| Étiquette | Sens |
|---|---|
| `[CHANGEMENT]` | Comportement volontairement différent de l'application Python. |
| `[CORRECTION]` | Bug de l'application Python, corrigé dans la réécriture. |
| `[INDICATIF]` | Valeur actuelle (couleur, taille, libellé, seuil), donnée comme repère. Le design est libre de la modifier. |

Toute exigence sans étiquette est imposée.

Chaque exigence porte un identifiant (`EQ-05`, `SE-04`…) et, quand c'est utile, la source Python qu'elle décrit (`session.py:89`). Ces sources restent consultables dans l'historique git après la suppression du code Python.

## Fichiers

| Fichier | Contenu |
|---|---|
| [01-equipe.md](01-equipe.md) | Vue Équipe : ajout, suppression et ordre des Membres |
| [02-icones.md](02-icones.md) | Choix d'une Icône, import d'image, couleur dominante |
| [03-presence.md](03-presence.md) | Vue Présence : choix des Participants, mémoire des Absents |
| [04-session.md](04-session.md) | Session : Tuiles, Tirage, annulation, Célébration |
| [05-fenetre-ecran.md](05-fenetre-ecran.md) | Fenêtre, premier plan, calage à droite, DPI, multi-écran |
| [06-persistance.md](06-persistance.md) | Dossier de données, format `team.json`, données embarquées |
| [07-performance.md](07-performance.md) | Budgets de performance et règles de conception |
| [08-distribution.md](08-distribution.md) | Plateforme, exe portable, construction |

## Périmètre

La réécriture couvre : la parité avec l'application Python, 2 changements (mémoire des Absents, Tirage qui exclut le Désigné) et les corrections de bugs listées plus bas.

Hors périmètre :

- mise à jour automatique ;
- traduction (interface en français uniquement) ;
- thème clair ;
- renommage d'un Membre (`rename_member` était du code mort, sans interface) ;
- migration du format `team.json` v1 ;
- Linux et macOS ;
- toute nouvelle fonctionnalité. Les idées vont dans une liste « après la parité ».

## Design

Le visuel est libre (couleurs, typographie, formes, animations, disposition des vues Équipe et Présence, fenêtre de choix d'Icône, barre de titre). Les contraintes fonctionnelles suivantes restent imposées. Elles sont détaillées dans les fichiers concernés :

- En Session, la fenêtre est une colonne collée au bord droit de l'écran, sur toute la hauteur de la zone de travail.
- Sa largeur s'adapte au nom le plus long, dans la limite de 18 % de la largeur de l'écran.
- Tous les Restants sont visibles sans défilement, et les Tuiles se partagent la hauteur.
- Un affichage compact (Icône seule) prend le relais quand les Tuiles sont trop petites.
- Chaque Tuile est teintée avec la couleur dominante de l'image du Membre.
- Le Désigné se repère au premier coup d'œil.
- Une Célébration s'affiche, puis l'application se ferme.
- L'option « toujours au premier plan » existe.
- L'application utilise uniquement un thème sombre.

Des maquettes sont produites et validées après cette spécification, avant l'écriture du code.

## Vérification

- Tests unitaires : logique de Session et couleur dominante en TypeScript (vitest), persistance en Rust (`cargo test`).
- Tests de bout en bout Playwright sur l'interface web, avec l'IPC Tauri simulé. Ils couvrent les parcours Équipe, Présence et Session.
- Recette manuelle : DPI, multi-écran, premier plan, démarrage de l'exe, fermeture après la Célébration.

Chaque exigence de cette spécification doit être couverte par au moins un test automatique ou une ligne de recette manuelle.

## Corrections de bugs

Toutes ces corrections portent l'étiquette `[CORRECTION]` dans leur fichier.

| Bug de l'application Python | Exigence |
|---|---|
| L'import SVG ne fonctionne pas dans l'exe | IC-14 |
| Les images de la vue Présence sont déformées | PR-03 |
| Le contrôle des doublons de noms tient compte de la casse | EQ-10 |
| « Valider » sans changement efface l'image d'un Membre | IC-07 |
| Un `team.json` illisible est écrasé à la première modification | PE-07 |
| ↩ reste désactivé tant que personne n'a parlé, même avec un Désigné | SE-08 |
| En Session, la fenêtre déborde probablement sous la barre des tâches | FE-08 |
| La mise en évidence du Désigné disparaît après un redimensionnement | SE-06 |

Les quatre bugs du milieu du tableau (image effacée, `team.json` écrasé, ↩ désactivé, débordement de la fenêtre) ont été trouvés en lisant le code, et leur correction a été validée à la relecture de la spec.
