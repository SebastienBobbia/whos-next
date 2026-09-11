import { expect, test } from "@playwright/test";
import { installTauriMock } from "./fixtures";

/**
 * Couleurs de référence des 18 avatars embarqués, calculées avec l'algorithme
 * de l'application Python (PIL, median cut en 8 couleurs, assombrissement).
 * La spec demande un résultat visuellement proche, pas identique (IC-15).
 */
const REFERENCE: Record<string, string> = {
  "ape-converti-depuis-svg.png": "#164f99",
  "abo-removebg-preview.png": "#688292",
  "aro.png": "#896951",
  "czh.png": "#314399",
  "cdu-removebg-preview.png": "#815c04",
  "jbl-removebg-preview.png": "#37363a",
  "jbr-converti-depuis-svg.png": "#2c7676",
  "ljo.png": "#990000",
  "mle-removebg-preview.png": "#707b6c",
  "mbo-converti-depuis-svg.png": "#006172",
  "npo2-removebg-preview.png": "#936119",
  "pbi-removebg-preview.png": "#2e4c15",
  "qro-removebg-preview.png": "#3c3f3f",
  "rdi.png": "#5b5b5b",
  "sda-converti-depuis-svg.png": "#3c3273",
  "sbo.png": "#977758",
  "vpe-removebg-preview.png": "#667b20",
  "yle-removebg-preview.png": "#2e6863",
};

/** Écart maximal toléré par canal, sur 255. */
const TOLERANCE = 40;

function rgb(hex: string): [number, number, number] {
  return [
    parseInt(hex.slice(1, 3), 16),
    parseInt(hex.slice(3, 5), 16),
    parseInt(hex.slice(5, 7), 16),
  ];
}

function distance(a: string, b: string): number {
  const [r1, g1, b1] = rgb(a);
  const [r2, g2, b2] = rgb(b);
  return Math.max(Math.abs(r1 - r2), Math.abs(g1 - g2), Math.abs(b1 - b2));
}

test("les teintes des Tuiles restent proches de celles de l'application Python (IC-15)", async ({
  page,
}) => {
  await installTauriMock(page);
  await page.goto("/");

  const computed = await page.evaluate(async (files: string[]) => {
    const { dominantColor } = await import("/src/lib/icons.ts");
    const out: Record<string, string> = {};
    for (const file of files) {
      const image = new Image();
      image.src = `/default_data/icons/${file}`;
      await image.decode();
      out[file] = dominantColor(image);
    }
    return out;
  }, Object.keys(REFERENCE));

  const drift = Object.entries(REFERENCE)
    .map(([file, reference]) => ({
      file,
      reference,
      obtenu: computed[file],
      ecart: distance(reference, computed[file]),
    }))
    .filter((row) => row.ecart > TOLERANCE);

  expect(drift, `Teintes trop éloignées :\n${JSON.stringify(drift, null, 2)}`).toEqual([]);
});
