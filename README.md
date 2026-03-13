# Who's Next?

Petite application de bureau pour les daily meetings : savoir qui a parlé et qui n'a pas encore parlé, pour des équipes de taille moyenne (~12 personnes).

## Fonctionnalités

- **Gestion d'équipe** : ajout/suppression des membres permanents (persisté en JSON)
- **Sélection des présents** : cocher les personnes présentes au daily du jour
- **Session live** : affichage en temps réel de qui n'a pas encore parlé / qui a parlé
- **Tirage au sort** : tirer aléatoirement le prochain intervenant (marqué automatiquement)
- **Marquage manuel** : cliquer sur un nom pour le marquer comme ayant parlé
- **Always-on-top** : la fenêtre reste au premier plan par-dessus Teams (désactivable)
- **Thème sombre** par défaut

## Prérequis

- Python 3.10+
- tkinter (inclus avec Python sur Windows)

## Installation

```bash
pip install -r requirements.txt
```

## Lancement

```bash
python main.py
```

## Créer un exécutable Windows (.exe)

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name "WhosNext" main.py
```

L'exécutable sera dans le dossier `dist/`.

## Structure du projet

```
whos-next/
├── main.py              # Point d'entrée
├── team_manager.py      # Gestion des membres (CRUD + JSON)
├── session.py           # Logique de session (présents, parlé, restants)
├── ui/
│   ├── __init__.py
│   ├── main_window.py   # Fenêtre principale + navigation
│   ├── team_view.py     # Vue gestion d'équipe
│   ├── setup_view.py    # Vue sélection des présents
│   └── session_view.py  # Vue live du meeting
├── data/
│   └── team.json        # Données locales (gitignored)
├── requirements.txt
└── .gitignore
```
