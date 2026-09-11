# 02 — Icônes

Une Icône est soit un emoji, soit une image importée. Un Membre peut ne pas avoir d'Icône. Ce fichier décrit la fenêtre de choix d'Icône, l'import des images et le calcul de la couleur dominante.

Sources Python : `ui/icon_picker.py`, `team_manager.py`, `ui/team_view.py` (`_open_image`), `ui/session_view.py` (`_dominant_color`).

## Fenêtre de choix d'Icône

**IC-01** — La fenêtre est modale : tant qu'elle est ouverte, la fenêtre principale ne réagit pas. Elle est centrée sur la fenêtre principale, sa taille est fixe, et son titre est `Icône — <nom du Membre>` `[INDICATIF]`. (`ui/icon_picker.py:109-134`, `ui/team_view.py:149`)

**IC-02** — La fenêtre propose une grille de 64 emojis, dans cet ordre (8 par ligne `[INDICATIF]`) : (`ui/icon_picker.py:17-87`)

- Visages : 😀 😎 🤓 😍 🤩 😜 🥸 🧐 😇 🤠 🥳 😈 👻 🤖 👽 🎃
- Animaux : 🐱 🐶 🦊 🐻 🐼 🐨 🐯 🦁 🐸 🐵 🦄 🐲 🦋 🐧 🦉 🦅
- Métiers et objets : 👨‍💻 👩‍💻 🧑‍🚀 👨‍🎨 👩‍🔬 🧑‍🍳 👨‍🎤 🧑‍🏫 ⚡ 🔥 💎 🌟 🎯 🚀 🎸 🎮
- Nature : 🌈 ☀️ 🌙 ⭐ ❄️ 🌊 🌸 🍀
- Divers : ❤️ 💙 💜 🖤 🤍 💛 🧡 💚

**IC-03** — À l'ouverture, la fenêtre montre l'Icône actuelle du Membre. Une Icône emoji est mise en évidence dans la grille. Pour une Icône image, le nom de son fichier est affiché dans la zone image. (`ui/icon_picker.py:127-131`)

**IC-04** — Un clic sur un emoji le sélectionne et annule le choix d'un fichier image. Un clic sur l'emoji déjà sélectionné le désélectionne. (`ui/icon_picker.py:252-269`)

**IC-05** — Le bouton `Parcourir…` `[INDICATIF]` ouvre le sélecteur de fichiers de Windows, titré `Choisir une image` `[INDICATIF]`. Deux filtres sont proposés : `Images` (`*.png *.jpg *.jpeg *.gif *.bmp *.webp *.svg`) et `Tous les fichiers` (`*.*`). Après un choix, la zone image affiche le nom du fichier et l'emoji sélectionné est désélectionné. Un nom de plus de 28 caractères est coupé à 25 caractères, suivi de `…`. Si on ferme le sélecteur sans choisir, rien ne change. (`ui/icon_picker.py:271-294`)

**IC-06** — Le bouton `Valider` ferme la fenêtre et applique le choix, dans cet ordre de priorité :
1. un fichier image a été choisi : il devient l'Icône image du Membre ;
2. sinon, un emoji est sélectionné : il devient l'Icône emoji du Membre ;
3. sinon : aucune modification. (`ui/icon_picker.py:301-310`)

**IC-07** `[CORRECTION]` — Valider sans avoir rien changé ne modifie pas l'Icône et ne supprime aucun fichier. Choisir comme nouvelle image un fichier qui se trouve déjà dans `icons\` fonctionne. Lors d'un remplacement, la nouvelle image est copiée avant que l'ancienne soit supprimée.
Python : la fenêtre renvoyait le nom du fichier stocké (`aro.png`) comme s'il s'agissait d'un nouveau fichier à importer (`ui/icon_picker.py:130`, `:303`). `set_icon` supprimait d'abord l'ancien fichier, puis tentait de copier `aro.png` depuis le dossier courant, ce qui échouait (`team_manager.py:153-161`). L'image était perdue.

**IC-08** — Le bouton `Annuler` et la fermeture de la fenêtre ne modifient rien. (`ui/icon_picker.py:230-239`)

**IC-09** — Le bouton `Supprimer l'icône` `[INDICATIF]` retire tout de suite l'Icône du Membre et ferme la fenêtre, sans passer par `Valider`. (`ui/icon_picker.py:296-299`)

**IC-10** — Tout changement d'Icône est sauvegardé immédiatement. La vue Équipe affiche la nouvelle Icône dès la fermeture de la fenêtre. (`team_manager.py:166`, `ui/team_view.py:152-155`)

## Import et stockage des images

**IC-11** — Une image importée est copiée dans le dossier `icons\` du dossier de données, sous son nom d'origine. Si ce nom est déjà pris, un suffixe numérique est ajouté avant l'extension : `photo.png` devient `photo_1.png`, puis `photo_2.png`, etc. Le Membre enregistre uniquement le nom du fichier, pas son chemin. (`team_manager.py:260-272`)

**IC-12** — Quand une Icône image est remplacée ou retirée, et quand son Membre est supprimé, l'ancien fichier est supprimé de `icons\`. Un échec de suppression est ignoré sans message. (`team_manager.py:153-155`, `:274-279`)

**IC-13** — Le fichier choisi est copié sans vérification de format. Une image illisible (fichier corrompu, format non géré) n'empêche pas l'application de fonctionner : le Membre s'affiche sans image, avec la couleur de Tuile par défaut. (`ui/session_view.py:320-328`, `ui/team_view.py:259-268`)

**IC-14** `[CORRECTION]` — Une image SVG s'affiche partout (vue Équipe, vue Présence, Session) et donne une couleur dominante.
Python : la conversion SVG passait par cairosvg, qui a besoin d'une DLL cairo absente de l'exe. La vue Présence n'appelait même pas la conversion SVG. (`ui/team_view.py:19-32`, `ui/setup_view.py:163`)

## Couleur dominante

**IC-15** — Une Icône image donne une couleur dominante, qui sert de fond à la Tuile du Membre en Session (voir SE-15). La méthode est imposée : (`ui/session_view.py:67-123`)

1. réduire l'image à 64 × 64 px ;
2. ne garder que les pixels assez opaques (alpha ≥ 128 sur 255) ;
3. réduire ces pixels à 8 couleurs par quantification « median cut » ;
4. prendre la couleur qui couvre le plus de pixels ;
5. l'assombrir en multipliant R, G et B par 0,6 `[INDICATIF]` ;
6. si sa luminance (0,299 R + 0,587 G + 0,114 B) dépasse encore 140 `[INDICATIF]`, la multiplier de nouveau par 0,6 `[INDICATIF]`.

Le résultat doit être visuellement proche de celui de l'application Python. Il n'a pas besoin d'être identique au pixel près. Les coefficients peuvent être ajustés au thème sombre retenu par le design.

**IC-16** — Si l'image n'a aucun pixel opaque ou si le calcul échoue, la Tuile prend la couleur par défaut. Une Icône emoji ou l'absence d'Icône donne aussi la couleur par défaut. (`ui/session_view.py:90-91`, `:122-123`, `:329-330`)
