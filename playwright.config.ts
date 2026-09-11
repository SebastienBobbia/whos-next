import { defineConfig, devices } from "@playwright/test";

/**
 * Tests de bout en bout sur l'interface web, avec l'IPC Tauri simulé
 * (voir e2e/fixtures.ts). Le DPI et le multi-écran restent en recette
 * manuelle : aucun outil ne les simule de façon fiable.
 */
export default defineConfig({
  testDir: "./e2e",
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 1 : 0,
  reporter: process.env.CI ? "line" : "list",
  use: {
    baseURL: "http://localhost:1420",
    viewport: { width: 420, height: 550 },
    trace: "on-first-retry",
  },
  projects: [{ name: "chromium", use: { ...devices["Desktop Chrome"] } }],
  webServer: {
    command: "npm run dev",
    url: "http://localhost:1420",
    reuseExistingServer: !process.env.CI,
    timeout: 60_000,
  },
});
