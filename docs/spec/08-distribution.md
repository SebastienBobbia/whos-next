# 08 — Plateforme et distribution

Sources Python : `WhosNext.spec`, `README.md` (partie « Données d'équipe embarquées »).

## Plateforme

**DI-01** — L'application tourne sur Windows 10 et Windows 11, en x64 uniquement.

**DI-02** — L'interface est uniquement en français.

## Livraison

**DI-03** — L'application est livrée sous forme d'un seul fichier `WhosNext.exe`, portable :
- pas d'installateur ;
- pas de droits administrateur ;
- pas de runtime à installer, à part WebView2, déjà présent sur Windows 11 et sur Windows 10 à jour.

Python : un dossier `dist\WhosNext\` contenant l'exe et de nombreux fichiers (`WhosNext.spec:104-113`).

**DI-04** — L'Équipe embarquée (PE-10) et le logo sont intégrés dans l'exe. Aucun fichier annexe n'est nécessaire.

**DI-05** — L'icône de l'exe et celle de la fenêtre utilisent le logo de l'application (`assets/logo.ico`, dont la source est `assets/logo.png`). (`WhosNext.spec:101`)

**DI-06** — Pour passer de l'ancienne application à la nouvelle, on remplace le dossier `dist\WhosNext\` par le nouvel exe. La nouvelle application reprend les données de `%APPDATA%\WhosNext\` telles quelles, sans aucune action de l'utilisateur.

**DI-07** — Si WebView2 est absent, l'application affiche un message qui explique qu'il faut installer « Microsoft Edge WebView2 Runtime », au lieu de se fermer sans rien dire.

## Construction

**DI-08** — Pour le développement et les tests, l'exe est construit sur le poste Windows, avec Rust, les VS Build Tools et Node. Un agent dans WSL pilote ces outils (`cargo.exe`, `npm.cmd`).

**DI-09** — L'exe destiné aux collègues est construit par GitHub Actions sur un runner `windows-latest`, déclenché par un tag de version.
