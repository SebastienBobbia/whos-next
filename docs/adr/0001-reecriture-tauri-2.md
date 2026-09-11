# Réécriture en Tauri 2

L'application Python (customtkinter + PyInstaller) rame sur Windows : démarrage lent, clic sur une Tuile lent, redimensionnement lent, et gel au passage sur un écran de DPI différent. Deux causes se cumulent. customtkinter dessine chaque widget sur un Canvas Tk piloté en Python. Et le code reconstruit tous les widgets à chaque action. Nous réécrivons l'application en Tauri 2 (cœur Rust, interface web dans WebView2). La maintenance se fait uniquement par agent IA. Tauri 2 produit un exe portable léger, sans runtime à installer sur Windows 10/11. WebView2 affiche les emojis en couleur et gère nativement le DPI par écran.

## Considered Options

- **Garder Python et corriger** : les corrections de cache et de rendu aident, mais customtkinter et le démarrage PyInstaller + Tcl/Tk restent lents par nature.
- **C# WPF** : n'affiche pas les emojis en couleur, et les Icônes emoji sont une fonctionnalité centrale.
- **C# WinUI 3** : le déploiement non packagé en exe portable est complexe.

## Consequences

La spec fonctionnelle (`docs/spec/`) est la seule référence de parité avec l'application Python. Le README n'est pas à jour et n'est pas une référence. La spec contient aussi des budgets de performance : un portage naïf reproduirait la reconstruction complète de l'interface à chaque action.
