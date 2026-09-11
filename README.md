# Who's Next?

Application de bureau pour les daily meetings : savoir qui n'a pas encore pris la parole. La fenêtre se colle au bord droit de l'écran, par-dessus Teams.

## Fonctionnalités

- **Équipe** : ajout, suppression et réordonnancement des membres permanents, avec une icône emoji ou une image par personne.
- **Présence** : cocher les personnes présentes au daily. Les personnes décochées reviennent décochées au daily suivant.
- **Session** : une tuile par personne restante, teintée par la couleur dominante de son avatar. Un clic marque la prise de parole.
- **Tirage au sort** : désigne au hasard quelqu'un qui n'a pas encore parlé, jamais la personne déjà désignée.
- **Annulation** : efface la désignation, puis rend leur tuile aux personnes déjà passées.
- **Toujours au premier plan**, activable et désactivable.
- **Thème sombre**, polices embarquées, aucun accès réseau.

## Pour les utilisateurs

Un seul fichier : `WhosNext.exe`. Pas d'installation, pas de droits administrateur. Windows 10 ou 11 en x64, avec Microsoft Edge WebView2 Runtime, présent de base sur Windows 11 et sur Windows 10 à jour.

Les données vivent dans `%APPDATA%\WhosNext\` : `team.json` et le dossier `icons\`. L'équipe embarquée dans l'exe n'y est copiée qu'au premier lancement ; ensuite, les modifications sont locales et ne sont jamais écrasées. Pour repartir de zéro, supprimer ce dossier avant de relancer.

**Mettre à jour l'équipe embarquée :** modifier `default_data/team.json` et `default_data/icons/`, puis reconstruire l'exe. Les collègues qui ont déjà lancé l'application gardent leurs données.

## Pour développer

Prérequis, côté Windows : Node 22 ou plus, Rust `stable-x86_64-pc-windows-msvc`, et les Visual Studio Build Tools avec la charge de travail C++.

```bash
npm install
npm run tauri dev      # application en développement, rechargement à chaud
npm run tauri build    # produit src-tauri/target/release/WhosNext.exe
```

Vérifications :

```bash
npm run check                                      # typage Svelte et TypeScript
npm test                                           # domaine Session (vitest)
npm run test:e2e                                   # parcours des vues (Playwright)
cargo test --manifest-path src-tauri/Cargo.toml    # persistance (Rust)
```

Les points non automatisables — DPI, multi-écran, premier plan, distribution — sont listés dans [docs/recette-manuelle.md](docs/recette-manuelle.md).

## Documentation

| Fichier | Contenu |
|---|---|
| [CONTEXT.md](CONTEXT.md) | Glossaire du domaine |
| [docs/spec/](docs/spec/) | Spécification fonctionnelle, une exigence par identifiant |
| [docs/adr/](docs/adr/) | Décisions structurantes et leurs alternatives écartées |
| [docs/recette-manuelle.md](docs/recette-manuelle.md) | Vérifications manuelles avant distribution |
| [docs/design/](docs/design/) | Maquettes et pistes visuelles |

## Structure

```
whos-next/
├── src/                  # Interface Svelte 5 + TypeScript
│   ├── App.svelte        # Navigation entre les trois vues
│   ├── lib/              # Domaine Session, état de l'Équipe, icônes, glyphes
│   └── views/            # Équipe, Présence, Session, choix d'Icône
├── src-tauri/            # Cœur Rust
│   └── src/
│       ├── store.rs      # team.json, icônes, équipe embarquée
│       └── window.rs     # Zone de travail, calage, premier plan
├── e2e/                  # Tests Playwright
├── default_data/         # Équipe embarquée dans l'exe
└── docs/                 # Spec, ADR, recette, maquettes
```

> L'application Python d'origine (`main.py`, `ui/`, `WhosNext.spec`) est conservée le temps de valider la parité, puis sera supprimée.
