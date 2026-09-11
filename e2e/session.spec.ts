import { expect, type Page, test } from "@playwright/test";
import { calls, installTauriMock } from "./fixtures";

/** Ouvre une Session avec les 4 Membres de l'Équipe de test. */
async function startSession(page: Page) {
  await page.goto("/");
  await page.getByRole("button", { name: "Préparer le Daily" }).click();
  await page.getByRole("button", { name: "Tout cocher" }).click();
  await page.getByRole("button", { name: "Démarrer le Daily" }).click();
  await expect(page.getByTitle("Tirage au sort")).toBeVisible();
}

const tiles = (page: Page) => page.locator("li.tile");
const designated = (page: Page) => page.locator("li.tile.designated");

test.beforeEach(async ({ page }) => {
  await installTauriMock(page);
  await startSession(page);
});

test("affiche une Tuile par Restant, dans l'ordre de l'Équipe (SE-02)", async ({ page }) => {
  await expect(tiles(page)).toHaveCount(4);
  await expect(tiles(page).first()).toContainText("Adeline");
  await expect(tiles(page).last()).toContainText("Yoann");
});

test("cale la fenêtre au bord droit au démarrage (FE-07)", async ({ page }) => {
  const fits = (await calls(page)).filter((c) => c.cmd === "fit_to_right_edge");
  expect(fits).toHaveLength(1);
  expect(fits[0].args).toMatchObject({ minWidth: 90, maxWidthRatio: 0.18 });
});

test("retire la Tuile cliquée (SE-03)", async ({ page }) => {
  await tiles(page).filter({ hasText: "Marion" }).click();
  await expect(tiles(page)).toHaveCount(3);
  await expect(page.getByText("Marion")).toHaveCount(0);
});

test("le Tirage ne retombe jamais sur le Désigné (SE-04)", async ({ page }) => {
  const draw = page.getByTitle("Tirage au sort");
  await draw.click();
  await expect(designated(page)).toHaveCount(1);

  for (let i = 0; i < 8; i++) {
    const before = await designated(page).innerText();
    await draw.click();
    await expect(designated(page)).not.toHaveText(before);
  }
});

test("désactive le Tirage quand le seul Restant est le Désigné (SE-05)", async ({ page }) => {
  for (const name of ["Adeline", "Camille", "Marion"]) {
    await tiles(page).filter({ hasText: name }).click();
  }
  await expect(tiles(page)).toHaveCount(1);

  await page.getByTitle("Tirage au sort").click();
  await expect(designated(page)).toHaveCount(1);
  await expect(page.getByTitle("Tirage au sort")).toBeDisabled();
});

test("le clic sur une Tuile efface le Désigné (SE-03)", async ({ page }) => {
  await page.getByTitle("Tirage au sort").click();
  await tiles(page).first().click();
  await expect(designated(page)).toHaveCount(0);
});

test("l'annulation efface le Désigné, puis rend les Tuiles (SE-07, SE-08)", async ({ page }) => {
  const undo = page.getByTitle("Annuler");
  await expect(undo).toBeDisabled();

  await page.getByTitle("Tirage au sort").click();
  await expect(undo).toBeEnabled();
  await undo.click();
  await expect(designated(page)).toHaveCount(0);
  await expect(tiles(page)).toHaveCount(4);

  await tiles(page).filter({ hasText: "Camille" }).click();
  await expect(tiles(page)).toHaveCount(3);
  await undo.click();
  await expect(tiles(page)).toHaveCount(4);
  await expect(tiles(page).nth(1)).toContainText("Camille");
});

test("termine la Session et revient à l'Équipe (SE-09, FE-10)", async ({ page }) => {
  await page.getByTitle("Terminer").click();
  await expect(page.getByRole("heading", { name: "Gestion de l'équipe" })).toBeVisible();
  const restores = (await calls(page)).filter((c) => c.cmd === "restore_window");
  expect(restores.at(-1)?.args).toMatchObject({ width: 420, height: 550 });
});

test("affiche la Célébration puis ferme l'application (SE-10)", async ({ page }) => {
  for (const name of ["Adeline", "Camille", "Marion", "Yoann"]) {
    await tiles(page).filter({ hasText: name }).click();
  }
  await expect(page.getByText("Tout le monde")).toBeVisible();
  await expect(page.getByTitle("Tirage au sort")).toBeDisabled();
  await expect(page.getByTitle("Annuler")).toBeDisabled();

  await expect
    .poll(async () => (await calls(page)).filter((c) => c.cmd === "quit_app").length, {
      timeout: 3000,
    })
    .toBe(1);
});
