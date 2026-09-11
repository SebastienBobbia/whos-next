# 01 — Vue Équipe

La vue Équipe sert à gérer la liste des Membres. C'est la vue affichée au lancement de l'application.

Sources Python : `ui/team_view.py`, `team_manager.py`, `ui/main_window.py`.

## Affichage

**EQ-01** — Au lancement, l'application affiche la vue Équipe. (`ui/main_window.py:82`)

**EQ-02** — La vue affiche les Membres dans l'ordre de l'Équipe. Chaque ligne contient, dans cet ordre `[INDICATIF]` : une poignée de réordonnancement, l'Icône du Membre (si elle existe), son numéro de position à partir de 1 et son nom (`3. Camille`), un bouton Icône, un bouton de suppression. (`ui/team_view.py:182-245`)

**EQ-03** — Le bouton Icône montre l'état de l'Icône du Membre : l'emoji lui-même pour une Icône emoji, un pictogramme d'image pour une Icône image (`🖼` `[INDICATIF]`), un signe d'ajout pour un Membre sans Icône (`＋` `[INDICATIF]`). (`ui/team_view.py:213-215`)

**EQ-04** — Une Icône image s'affiche en conservant ses proportions, dans un carré de 24 px `[INDICATIF]`. Si le fichier image est introuvable ou illisible, la ligne s'affiche sans Icône, sans message d'erreur. Le bouton Icône garde alors le pictogramme d'image. (`ui/team_view.py:247-269`)

**EQ-05** — Un compteur affiche le nombre de Membres : `18 membre(s) dans l'équipe` `[INDICATIF]`. (`ui/team_view.py:180`)

**EQ-06** — Quand l'Équipe est vide, la liste affiche `Aucun membre. Ajoutez des personnes ci-dessus.` `[INDICATIF]` et l'indication de réordonnancement est masquée. (`ui/team_view.py:167-174`)

## Ajout

**EQ-07** — Un champ de saisie (texte d'aide `Nom du membre...` `[INDICATIF]`) et un bouton `Ajouter` permettent d'ajouter un Membre. La touche Entrée dans le champ équivaut au bouton. (`ui/team_view.py:76-85`)

**EQ-08** — Le nom saisi est débarrassé de ses espaces de début et de fin. Le Membre est ajouté à la fin de l'Équipe, sans Icône. Après un ajout réussi, le champ est vidé, le message d'erreur est effacé et l'Équipe est sauvegardée. (`ui/team_view.py:124-136`, `team_manager.py:101-112`)

**EQ-09** — Si le nom est vide après retrait des espaces, le message `Veuillez entrer un nom.` `[INDICATIF]` s'affiche et rien n'est ajouté. (`ui/team_view.py:127-129`)

**EQ-10** `[CORRECTION]` — Un nom déjà présent dans l'Équipe est refusé. La comparaison ignore la casse (« Alice », « alice » et « ALICE » sont le même nom) mais pas les accents (« Loïc » et « Loic » sont deux noms différents). Le message `"<nom saisi>" existe déjà dans l'équipe.` `[INDICATIF]` s'affiche et rien n'est ajouté. Des noms qui ne diffèrent que par la casse et qui existent déjà dans `team.json` sont chargés tels quels, sans erreur.
Python : la comparaison tenait compte de la casse. (`team_manager.py:106`)

**EQ-11** — Le message d'erreur reste affiché jusqu'au prochain ajout réussi. (`ui/team_view.py:131-136`)

## Suppression

**EQ-12** — Le bouton de suppression retire immédiatement le Membre, sans demander de confirmation. Si le Membre avait une Icône image, son fichier est supprimé du dossier `icons\`. La numérotation est mise à jour et l'Équipe est sauvegardée. (`ui/team_view.py:138-141`, `team_manager.py:114-124`)

## Réordonnancement

**EQ-13** — On change la position d'un Membre par glisser-déposer : on maintient le clic sur la ligne (ou sa poignée) et on la fait glisser. Pendant le glissement, la ligne déplacée est mise en évidence, et un indicateur montre où elle sera insérée. Au relâchement, le Membre est inséré à l'endroit indiqué, la numérotation est mise à jour et l'Équipe est sauvegardée. (`ui/team_view.py:273-329`)

**EQ-14** — Relâcher la ligne à sa position d'origine ne change pas l'ordre.

**EQ-15** — Le glisser-déposer ne démarre pas depuis le bouton Icône ni depuis le bouton de suppression. Un clic sur ces boutons déclenche leur action.

**EQ-16** — Quand l'Équipe n'est pas vide, une indication explique le glisser-déposer : `⠿ Maintenir et glisser pour réordonner` `[INDICATIF]`. (`ui/team_view.py:94-100`)

## Navigation

**EQ-17** — Le bouton Icône d'un Membre ouvre la fenêtre de choix d'Icône pour ce Membre (voir [02-icones.md](02-icones.md)). (`ui/team_view.py:143-155`)

**EQ-18** — Le bouton `Préparer le Daily >>>` `[INDICATIF]` ouvre la vue Présence (voir [03-presence.md](03-presence.md)). Quand l'Équipe est vide, ce bouton n'a aucun effet et aucun message ne s'affiche. (`ui/main_window.py:100-103`)
