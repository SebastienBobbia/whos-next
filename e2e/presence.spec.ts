import { expect, test } from "@playwright/test";
import { installTauriMock, storedMembers } from "./fixtures";

test.beforeEach(async ({ page }) => {
  await installTauriMock(page);
  await page.goto("/");
  await page.getByRole("button", { name: "Préparer le Daily" }).click();
});

test("décoche les Absents du dernier daily et coche les autres (PR-04)", async ({ page }) => {
  await expect(page.getByRole("checkbox", { name: "Adeline" })).toBeChecked();
  await expect(page.getByRole("checkbox", { name: "Camille" })).toBeChecked();
  await expect(page.getByRole("checkbox", { name: "Yoann" })).not.toBeChecked();
  await expect(page.getByText("3/4 présents")).toBeVisible();
});

test("met le compteur à jour (PR-05)", async ({ page }) => {
  await page.getByRole("checkbox", { name: "Marion" }).uncheck();
  await expect(page.getByText("2/4 présents")).toBeVisible();
  await page.getByRole("checkbox", { name: "Yoann" }).check();
  await expect(page.getByText("3/4 présents")).toBeVisible();
});

test("coche et décoche tout (PR-06)", async ({ page }) => {
  await page.getByRole("button", { name: "Tout décocher" }).click();
  await expect(page.getByText("0/4 présents")).toBeVisible();
  await page.getByRole("button", { name: "Tout cocher" }).click();
  await expect(page.getByText("4/4 présents")).toBeVisible();
});

test("ne lance rien quand personne n'est coché (PR-08)", async ({ page }) => {
  await page.getByRole("button", { name: "Tout décocher" }).click();

  await expect(page.getByText("0/4 présents")).toBeVisible();
  await expect(page.getByRole("button", { name: "Démarrer le Daily" })).toBeDisabled();
  await expect(page.getByRole("heading", { name: "Qui est présent ?" })).toBeVisible();
});

test("enregistre les Absents au lancement de la Session (PR-09)", async ({ page }) => {
  await page.getByRole("checkbox", { name: "Camille" }).uncheck();
  await page.getByRole("checkbox", { name: "Yoann" }).check();
  await page.getByRole("button", { name: "Démarrer le Daily" }).click();

  const members = await storedMembers(page);
  expect(members.find((m) => m.name === "Camille")?.absent).toBe(true);
  expect(members.find((m) => m.name === "Yoann")?.absent).toBeUndefined();
  expect(members.find((m) => m.name === "Adeline")?.absent).toBeUndefined();
});

test("revient à l'Équipe sans rien enregistrer (PR-07)", async ({ page }) => {
  await page.getByRole("checkbox", { name: "Adeline" }).uncheck();
  await page.getByRole("button", { name: "Retour" }).click();

  await expect(page.getByRole("heading", { name: "Gestion de l'équipe" })).toBeVisible();
  const members = await storedMembers(page);
  expect(members.find((m) => m.name === "Adeline")?.absent).toBeUndefined();
});
