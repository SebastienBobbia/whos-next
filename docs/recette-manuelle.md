# Recette manuelle

Ces vérifications ne sont pas automatisables de façon fiable : elles touchent au DPI, au multi-écran, au comportement de la fenêtre et à la distribution. Le reste de la spec est couvert par `npm test` (domaine et persistance) et `npm run test:e2e` (parcours des vues).

À passer avant chaque version distribuée aux collègues.

## Démarrage et fenêtre

| # | Vérification | Attendu | Spec |
|---|---|---|---|
| R-01 | Lancer `WhosNext.exe` | La vue Équipe s'affiche en moins d'une seconde | PF-01 |
| R-02 | Regarder la barre des tâches et le coin de la fenêtre | Le logo de l'application, pas une icône générique | DI-05, FE-01 |
| R-03 | Ouvrir Teams, puis l'application | La fenêtre reste au-dessus de Teams | FE-05 |
| R-04 | Décocher « Toujours au premier plan », cliquer dans Teams | La fenêtre passe derrière | FE-05 |
| R-05 | Recocher, lancer une Session, la terminer avec ■ | La case revient cochée ou décochée comme avant la Session, et son effet est conservé | FE-06 |
| R-06 | Fermer la fenêtre avec la croix | L'application se termine sans confirmation | FE-04 |

## Calage et écrans

| # | Vérification | Attendu | Spec |
|---|---|---|---|
| R-10 | Lancer une Session | La fenêtre forme une colonne collée au bord droit, sur toute la hauteur | FE-07 |
| R-11 | Regarder le bas de la colonne | Elle ne passe pas sous la barre des tâches, barre de titre comprise | FE-08 |
| R-12 | Session avec un nom très long, puis marquer cette personne, puis cliquer ↔ | La colonne rétrécit seulement au clic sur ↔ | FE-09 |
| R-13 | Déplacer la fenêtre sur un écran de DPI différent (100 % et 150 %) | Aucun gel, l'interface garde sa taille logique, nouvelle mise en page en moins de 200 ms | FE-13, PF-03 |
| R-14 | Sur ce second écran, cliquer ↔ | La colonne se colle au bord droit de **cet** écran, sous sa barre des tâches | FE-14 |
| R-15 | Cliquer ↔ plusieurs fois de suite | Réaction immédiate, moins de 100 ms, sans clignotement | PF-04 |

## Session

| # | Vérification | Attendu | Spec |
|---|---|---|---|
| R-20 | Session à 20 Participants sur un écran 1080p | Toutes les Tuiles visibles sans défilement, affichage compact avec l'avatar seul | SE-12, SE-14 |
| R-21 | Cliquer une Tuile | Elle disparaît immédiatement, moins de 50 ms de latence perçue | SE-03, PF-02 |
| R-22 | Cliquer 🎲 | L'anneau jaune clignote 3 fois puis reste affiché | SE-06 |
| R-23 | Redimensionner la fenêtre pendant qu'une personne est Désignée | L'anneau reste visible | SE-06 |
| R-24 | Regarder le fond des Tuiles | Chaque Tuile est teintée par la couleur dominante de l'avatar | SE-15, IC-15 |
| R-25 | Marquer la dernière personne | Célébration, puis fermeture de l'application au bout d'une seconde | SE-10 |

## Icônes et données

| # | Vérification | Attendu | Spec |
|---|---|---|---|
| R-30 | Bouton Icône, puis « Parcourir… », choisir un PNG | Le sélecteur Windows s'ouvre, l'image s'affiche dans la liste après validation | IC-05, IC-11 |
| R-31 | Même manipulation avec un SVG | L'image s'affiche partout, y compris en Session | IC-14 |
| R-32 | Rouvrir le choix d'Icône d'un Membre à image, cliquer « Valider » sans rien changer | L'image est toujours là, le fichier n'a pas été supprimé | IC-07 |
| R-33 | Remplacer l'image d'un Membre, puis regarder `%APPDATA%\WhosNext\icons\` | Le nouveau fichier existe, l'ancien a disparu | IC-12 |
| R-34 | Supprimer `%APPDATA%\WhosNext\`, relancer | L'Équipe embarquée revient, avec ses 18 Membres et leurs avatars | PE-11 |
| R-35 | Mettre un `team.json` invalide, lancer, ajouter un Membre | Équipe vide au départ, et le fichier d'origine conservé sous `team.json.illisible-…` | PE-07 |
| R-36 | Lancer l'ancienne application Python sur un `team.json` écrit par la nouvelle | L'Équipe est lue normalement, seule la marque des Absents est perdue | PE-05 |

## Distribution

| # | Vérification | Attendu | Spec |
|---|---|---|---|
| R-40 | Copier le seul `WhosNext.exe` sur un autre poste, sans installation ni droits admin | L'application démarre | DI-03 |
| R-41 | Sur un poste dont l'Équipe existe déjà | Les Membres et avatars sont repris sans action | DI-06 |
| R-42 | Sur un poste sans WebView2 | Un message explique qu'il faut installer WebView2 Runtime | DI-07 |
