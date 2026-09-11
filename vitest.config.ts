import { defineConfig } from "vitest/config";

/**
 * Configuration séparée de vite.config.ts : vitest embarque sa propre copie de
 * vite, et mélanger les deux jeux de types casse le typage du plugin Svelte.
 * Ce fichier ne déclare aucun plugin, donc le conflit disparaît.
 *
 * vitest ne prend que les tests unitaires : e2e/ appartient à Playwright.
 */
export default defineConfig({
  test: {
    include: ["src/**/*.test.ts"],
  },
});
