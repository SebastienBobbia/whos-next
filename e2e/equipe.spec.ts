import { expect, test } from "@playwright/test";
import { installTauriMock, storedMembers, TEAM } from "./fixtures";

test.beforeEach(async ({ page }) => {
  await installTauriMock(page);
  await page.goto("/");
});

test("affiche l'Équipe chargée, numérotée et comptée (EQ-02, EQ-05)", async ({ page }) => {
  await expect(page.getByText("1. Adeline")).toBeVisible();
  await expect(page.getByText("4. Yoann")).toBeVisible();
  await expect(page.getByText(`${TEAM.length} membres dans l'équipe`)).toBeVisible();
});

test("ajoute un Membre à la fin et le sauvegarde (EQ-08)", async ({ page }) => {
  await page.getByPlaceholder("Nom du membre...").fill("  Nicolas  ");
  await page.getByRole("button", { name: "Ajouter" }).click();

  await expect(page.getByText("5. Nicolas")).toBeVisible();
  const members = await storedMembers(page);
  expect(members.at(-1)).toMatchObject({ name: "Nicolas", icon_type: "", icon_value: "" });
});

test("refuse un nom vide (EQ-09)", async ({ page }) => {
  await page.getByPlaceholder("Nom du membre...").fill("   ");
  await page.getByRole("button", { name: "Ajouter" }).click();

  await expect(page.getByText("Veuillez entrer un nom.")).toBeVisible();
  expect(await storedMembers(page)).toHaveLength(TEAM.length);
});

test("refuse un doublon sans tenir compte de la casse (EQ-10)", async ({ page }) => {
  await page.getByPlaceholder("Nom du membre...").fill("adeline");
  await page.getByPlaceholder("Nom du membre...").press("Enter");

  await expect(page.getByText('"adeline" existe déjà dans l\'équipe.')).toBeVisible();
  expect(await storedMembers(page)).toHaveLength(TEAM.length);
});

test("accepte un nom qui ne diffère que par les accents (EQ-10)", async ({ page }) => {
  await page.getByPlaceholder("Nom du membre...").fill("Loic");
  await page.getByPlaceholder("Nom du membre...").press("Enter");
  await page.getByPlaceholder("Nom du membre...").fill("Loïc");
  await page.getByPlaceholder("Nom du membre...").press("Enter");

  const members = await storedMembers(page);
  expect(members.map((m) => m.name)).toContain("Loic");
  expect(members.map((m) => m.name)).toContain("Loïc");
});

test("supprime un Membre sans confirmation et renumérote (EQ-12)", async ({ page }) => {
  const row = page.locator("li.row").filter({ hasText: "Camille" });
  await row.getByTitle("Supprimer").click();

  await expect(page.getByText("Camille")).toHaveCount(0);
  await expect(page.getByText("2. Marion")).toBeVisible();
  expect(await storedMembers(page)).toHaveLength(TEAM.length - 1);
});

test("ouvre la vue Présence depuis le bouton du bas (EQ-18)", async ({ page }) => {
  await page.getByRole("button", { name: "Préparer le Daily" }).click();
  await expect(page.getByRole("heading", { name: "Qui est présent ?" })).toBeVisible();
});
