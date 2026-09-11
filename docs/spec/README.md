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

La réécriture couvre : la parité avec l'application Python, 2 changements (mémoire des Absents, Tirage qui exclut le Désigné) et 3 corrections (import SVG, proportions des images de la vue Présence, doublons de noms insensibles à la casse).

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

## Points à trancher

La lecture du code a révélé des bugs qui n'avaient pas été discutés. Chaque point porte une recommandation. Il faut trancher ces points avant de valider la spec.

**PT-1 — « Valider » sans changement efface l'image d'un Membre.**
Scénario : ouvrir la fenêtre de choix d'Icône d'un Membre qui a une Icône image, puis cliquer sur « Valider » sans rien changer. La fenêtre renvoie le nom du fichier stocké (`aro.png`) comme s'il s'agissait d'un nouveau fichier à importer (`ui/icon_picker.py:130`, `:303`). `set_icon` supprime d'abord l'ancien fichier, puis tente de copier `aro.png` depuis le dossier courant, ce qui échoue (`team_manager.py:153-161`). L'image est perdue. Le même problème se produit si on choisit avec « Parcourir… » un fichier qui se trouve déjà dans `icons\`.
Recommandation : corriger. « Valider » sans changement ne modifie rien. Lors d'un remplacement, copier la nouvelle image avant de supprimer l'ancienne.

**PT-2 — Un `team.json` illisible est écrasé.**
Si `team.json` contient du JSON invalide, l'application démarre avec une Équipe vide et écrase le fichier à la première modification (`team_manager.py:228-229`). L'Équipe est alors perdue définitivement. Avec l'abandon de la migration v1, un fichier dont la version n'est pas 2 tombe dans ce même cas.
Recommandation : corriger. Avant toute écriture, renommer le fichier illisible en `team.json.illisible-AAAAMMJJ-HHMMSS`, puis démarrer avec une Équipe vide.

**PT-3 — ↩ est désactivé tant que personne n'a parlé, même avec un Désigné.**
Scénario : lancer une Session, faire un Tirage, puis vouloir annuler ce Tirage. ↩ reste désactivé tant qu'aucun Participant n'A parlé (`ui/session_view.py:420`). La règle « ↩ efface d'abord le Désigné » ne s'applique donc qu'à partir du deuxième intervenant.
Recommandation : corriger. ↩ est actif dès qu'il y a un Désigné ou au moins un Participant qui A parlé.

**PT-4 — En Session, la fenêtre déborde sous la barre des tâches.**
Le calage passe à Tk la hauteur de la zone de travail comme hauteur de la zone client (`ui/session_view.py:266-272`). La barre de titre native vient s'y ajouter, et le bas de la fenêtre passe probablement sous la barre des tâches, de la hauteur de la barre de titre. Ce point est à confirmer lors de la recette de l'application actuelle.
Recommandation : corriger. La fenêtre entière, cadre compris, tient dans la zone de travail.
