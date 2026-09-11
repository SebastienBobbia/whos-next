# Who's Next?

Outil de bureau pour animer un daily : savoir, pendant la réunion, quels membres présents n'ont pas encore pris la parole.

## Language

### Équipe

**Équipe**:
Liste ordonnée et persistante des Membres.
_Avoid_: Liste, groupe

**Membre**:
Personne enregistrée dans l'Équipe, identifiée par un nom unique, avec une Icône optionnelle.
_Avoid_: Personne paramétrée, utilisateur, member

**Icône**:
Visuel optionnel d'un Membre : soit un emoji, soit une image importée.
_Avoid_: Avatar, photo

### Session

**Session**:
Un daily en cours, de son lancement jusqu'à sa fin.
_Avoid_: Meeting, réunion

**Participant**:
Membre coché présent pour une Session donnée.
_Avoid_: Présent, attendee

**Absent**:
Membre décoché lors du lancement d'une Session, qui reste décoché pour la suivante.
_Avoid_: Excusé, décoché, non-participant

**Restant**:
Participant qui n'a pas encore parlé dans la Session.
_Avoid_: Remaining, en attente

**A parlé**:
État d'un Participant dont la prise de parole est terminée dans la Session.
_Avoid_: Spoken, fait, passé

**Tirage**:
Désignation aléatoire d'un Restant comme prochain à parler.
_Avoid_: Random, dé, pick

**Désigné**:
Restant sélectionné par le dernier Tirage, pas encore marqué A parlé.
_Avoid_: Tiré, highlighted, surligné

**Tuile**:
Zone cliquable qui représente un Restant pendant la Session.
_Avoid_: Bouton, case, carte

**Célébration**:
Écran de fin affiché quand tous les Participants ont parlé, juste avant la fermeture de l'application.
_Avoid_: Animation de fin, écran final
