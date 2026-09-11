# 06 — Persistance

L'Équipe, les Icônes image et la marque des Absents sont enregistrées sur le poste de l'utilisateur. La Session et l'état « toujours au premier plan » ne sont jamais enregistrés.

Sources Python : `team_manager.py`.

## Dossier de données

**PE-01** — Les données sont dans `%APPDATA%\WhosNext\`. Au lancement, l'application crée ce dossier et son sous-dossier `icons\` s'ils n'existent pas. (`team_manager.py:40-67`)

Le dossier de secours Linux et macOS (`~/.whonext`) n'est pas repris : l'application tourne uniquement sous Windows.

## Format de `team.json`

**PE-02** — L'Équipe est enregistrée dans `%APPDATA%\WhosNext\team.json`, dans ce format :

```json
{
  "version": 2,
  "members": [
    { "name": "Alice", "icon_type": "emoji", "icon_value": "🐱" },
    { "name": "Bob", "icon_type": "image", "icon_value": "bob.png", "absent": true },
    { "name": "Charlie", "icon_type": "", "icon_value": "" }
  ]
}
```

- L'ordre du tableau `members` est l'ordre de l'Équipe.
- `icon_type` vaut `"emoji"`, `"image"` ou `""` (pas d'Icône).
- `icon_value` contient l'emoji, ou le nom d'un fichier du dossier `icons\`, ou `""`.
- `[CHANGEMENT]` `absent` est un booléen facultatif. Il n'est écrit que s'il vaut `true`. Un champ manquant ou `false` veut dire que le Membre n'est pas Absent. Voir [ADR 0002](../adr/0002-absents-dans-team-json-v2.md).
- `version` reste à `2`. Ne jamais l'incrémenter : l'ancienne application viderait l'Équipe (ADR 0002).

(`team_manager.py:8-16`, `:231-242`)

**PE-03** — Le fichier est écrit en UTF-8, avec une indentation de 2 espaces. Les caractères non ASCII (accents, emojis) sont écrits tels quels, sans séquence `\u`. (`team_manager.py:233-242`)

**PE-04** — Au chargement, un Membre sans `name` ou avec un `name` vide est ignoré. Un `icon_type` ou un `icon_value` absent vaut `""`. Les champs inconnus sont ignorés. (`team_manager.py:205-216`)

**PE-05** — Un fichier écrit par la nouvelle application doit rester lisible par l'application Python. L'application Python supprime le champ `absent` à sa prochaine écriture : c'est accepté.

**PE-06** `[CHANGEMENT]` — Il n'y a pas de migration depuis le format v1 (`{"members": ["Alice", "Bob"]}`). Un fichier dont `version` ne vaut pas `2` est traité comme un fichier illisible (PE-07).
Python : un fichier v1 était migré automatiquement. (`team_manager.py:217-226`)

**PE-07** — Si `team.json` est illisible (JSON invalide, structure inattendue ou version différente de 2), l'application démarre avec une Équipe vide. Dans l'application Python, le fichier est ensuite écrasé à la première modification. Ce comportement est à revoir : voir PT-2 dans le [README](README.md). (`team_manager.py:228-229`)

## Écriture

**PE-08** — `team.json` est entièrement réécrit, immédiatement, après chaque modification :
- ajout d'un Membre ;
- suppression d'un Membre ;
- réordonnancement ;
- changement d'Icône ;
- lancement d'une Session (enregistrement des Absents, PR-09).

(`team_manager.py:111`, `:122`, `:134`, `:166`, `:185`)

**PE-09** — Les fichiers image sont gérés comme décrit dans IC-11 et IC-12 : copie à l'import, suppression au remplacement, au retrait de l'Icône et à la suppression du Membre.

## Données embarquées

**PE-10** — L'exe embarque une Équipe par défaut : le contenu actuel de `default_data/team.json` (18 Membres) et de `default_data/icons/` (18 images PNG). (`WhosNext.spec:12`)

**PE-11** — Au lancement, si `team.json` n'existe pas, l'application copie l'Équipe embarquée (`team.json` et toutes les images) dans le dossier de données, puis la charge. Si `team.json` existe, même avec une Équipe vide, rien n'est copié. Les données d'un utilisateur ne sont donc jamais écrasées par l'Équipe embarquée. Pour repartir de l'Équipe embarquée, il faut supprimer `%APPDATA%\WhosNext\` avant de relancer l'application. (`team_manager.py:195-199`, `:244-256`)

**PE-12** — Pour mettre à jour l'Équipe embarquée, on modifie `default_data/`, puis on reconstruit l'exe. Les collègues qui ont déjà lancé l'application gardent leurs données locales.
