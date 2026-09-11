# Absents stockés dans team.json sans changer de version

La nouvelle application mémorise les Absents d'une Session à l'autre. Nous stockons cette information dans un booléen optionnel `absent` sur chaque Membre de `team.json`. Un champ manquant veut dire que le Membre est présent. Le champ `"version"` reste volontairement à `2`.

L'ancienne application Python traite toute version différente de 2 comme le format v1. Elle ignore alors tous les Membres, qui ne sont pas des chaînes, puis réécrit immédiatement le fichier avec une Équipe vide. Passer à `"version": 3` ferait donc perdre toute son Équipe à un collègue qui relance l'ancien exe. En gardant la version 2, l'ancienne app se contente de supprimer le champ `absent` à la prochaine écriture : on perd la mémoire des Absents, jamais l'Équipe.

## Considered Options

- **Fichier séparé `presence.json`** : `team.json` restait intact, mais nous avons préféré garder toutes les données d'un Membre au même endroit.
- **`"version": 3`** : rejeté, à cause de la perte de l'Équipe décrite plus haut.
