# 04 — Session

Une Session est un daily en cours. Elle affiche une Tuile pour chaque Restant et se termine par la Célébration, quand tous les Participants ont parlé.

Sources Python : `session.py`, `ui/session_view.py`.

## Déroulement

**SE-01** — Une Session démarre avec ses Participants, dans l'ordre de l'Équipe. Au départ, tous les Participants sont Restants et il n'y a pas de Désigné. La Session n'existe qu'en mémoire : elle n'est jamais sauvegardée. (`session.py:14-22`, `ui/session_view.py:218-225`)

**SE-02** — Seuls les Restants sont affichés, avec une Tuile chacun, dans l'ordre de l'Équipe. Un Participant qui A parlé disparaît de l'affichage. Aucun compteur n'est affiché. (`session.py:36-39`, `ui/session_view.py:407-429`)

**SE-03** — Un clic n'importe où sur une Tuile marque son Participant comme A parlé, et sa Tuile disparaît. Si un Désigné existe, il est effacé, même si la Tuile cliquée est celle d'un autre Restant. (`ui/session_view.py:346-351`)

**SE-04** `[CHANGEMENT]` — Le bouton Tirage (🎲 `[INDICATIF]`) choisit au hasard, avec une probabilité égale, un Restant autre que le Désigné actuel. Ce Restant devient le Désigné. Le Tirage ne le marque pas A parlé : il faut toujours cliquer sur sa Tuile.
Python : un Tirage pouvait retomber sur le Désigné actuel. (`session.py:89-101`, `ui/session_view.py:353-361`)

**SE-05** `[CHANGEMENT]` — Le bouton Tirage est désactivé quand le seul Restant est déjà le Désigné, et quand il n'y a plus de Restant.
Python : le bouton n'était désactivé qu'en fin de Session. (`ui/session_view.py:423`, `:428`)

**SE-06** — Le Désigné se repère au premier coup d'œil. Sa Tuile garde sa mise en évidence tant qu'il reste Désigné, y compris après un redimensionnement de la fenêtre ou un calage. Au moment du Tirage, une animation brève attire l'attention sur lui. Dans l'application Python `[INDICATIF]` : fond vert `#1a5c2a`, nom vert `#4ADE80` en gras, bordure jaune `#FACC15` qui clignote 3 fois (6 étapes de 150 ms) puis reste affichée. (`ui/session_view.py:363-392`, `:522-528`)
Python : la bordure jaune disparaissait au premier redimensionnement, parce que la Tuile était reconstruite sans elle.

**SE-07** — Le bouton d'annulation (↩ `[INDICATIF]`) agit ainsi :
- s'il y a un Désigné : il efface seulement le Désigné ;
- sinon : le dernier Participant marqué A parlé redevient Restant, et sa Tuile réapparaît à sa place dans l'ordre de l'Équipe.

On peut répéter l'annulation jusqu'à ce qu'il ne reste plus aucun Participant qui A parlé. (`session.py:103-113`, `ui/session_view.py:394-403`)

**SE-08** — Le bouton d'annulation est actif quand au moins un Participant A parlé, et désactivé sinon, même s'il y a un Désigné. Ce comportement est à revoir : voir PT-3 dans le [README](README.md). (`ui/session_view.py:420`)

**SE-09** — Le bouton de fin (■ `[INDICATIF]`) termine la Session immédiatement, sans confirmation. La Session est perdue et l'application revient à la vue Équipe (voir FE-10). (`ui/session_view.py:192-200`, `ui/main_window.py:121-123`)

**SE-10** — Quand le dernier Restant A parlé, la Célébration s'affiche :
- un grand message `Tout le monde a parlé ! 🎉` `[INDICATIF]`, dont la taille s'adapte à la fenêtre ;
- une animation pulsée `[INDICATIF : texte jaune #FFD600 sur fond noir, qui alterne avec #997F00 toutes les 250 ms]` ;
- les boutons Tirage et annulation sont désactivés ;
- **l'application se ferme** (fin du processus) 1 seconde après l'apparition de la Célébration.

(`ui/session_view.py:422-426`, `:431-479`)

## Barre d'actions

**SE-11** — Pendant la Session, 4 actions restent toujours visibles au-dessus des Tuiles : calage (↔, voir FE-06), Tirage, annulation et fin. Dans l'application Python, ce sont 4 petits boutons alignés de gauche à droite, dans cet ordre `[INDICATIF]`. (`ui/session_view.py:153-203`)

## Tuiles

**SE-12** — Tous les Restants sont visibles sans défilement. Les Tuiles occupent toute la largeur disponible et se partagent la hauteur à parts égales. Dans l'application Python `[INDICATIF]` : hauteur d'une Tuile = max(24, (hauteur disponible − 4 × n) / n), avec n le nombre de Restants. (`ui/session_view.py:483-513`)

**SE-13** — Le contenu d'une Tuile dépend de l'Icône du Membre : image + nom, emoji + nom, ou nom seul. Dans l'application Python `[INDICATIF]` : l'image est dans le coin supérieur gauche, de côté max(12, hauteur de Tuile / 4) ; l'emoji est à gauche ; le nom est centré ; la taille du texte vaut environ 55 % de la hauteur de la Tuile, limitée à largeur / 5, avec un minimum de 9. (`ui/session_view.py:530-570`, `:622-704`)

**SE-14** — Quand les Tuiles deviennent trop basses pour un nom lisible (moins de 48 px dans l'application Python `[INDICATIF]`), elles passent en affichage compact et ne montrent plus que l'Icône : l'image, l'emoji, ou, pour un Membre sans Icône, l'initiale de son nom en majuscule. (`ui/session_view.py:515-516`, `:572-620`)

**SE-15** — Le fond d'une Tuile est choisi dans cet ordre :
1. la couleur du Désigné, si le Participant est le Désigné ;
2. sinon, la couleur dominante de son Icône image (voir IC-15) ;
3. sinon, la couleur par défaut (`#2d2d44` `[INDICATIF]`).

(`ui/session_view.py:522-528`)

**SE-16** — Quand la taille de la fenêtre change pendant la Session (redimensionnement à la main, calage, changement d'écran), les Tuiles se recalculent : hauteur, taille du texte, passage en affichage compact ou retour à l'affichage normal. (`ui/session_view.py:205-210`)
