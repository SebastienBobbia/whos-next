/**
 * Chargement des Icônes image et calcul de leur couleur dominante (IC-15, IC-16).
 *
 * Chaque fichier n'est lu et décodé qu'une seule fois : le résultat est mis en
 * cache et réutilisé par toutes les vues (PF-11, PF-12).
 */
import { invoke } from "@tauri-apps/api/core";

export const TILE_DEFAULT = "#2d2d44";

export type LoadedIcon = {
  /** data URL prête pour un <img> */
  url: string;
  /** couleur dominante assombrie, ou TILE_DEFAULT */
  color: string;
};

const cache = new Map<string, Promise<LoadedIcon | null>>();

/** Charge une Icône image depuis le dossier icons\, ou null si elle est illisible (IC-13). */
export function loadIcon(filename: string): Promise<LoadedIcon | null> {
  const hit = cache.get(filename);
  if (hit) return hit;

  const task = (async (): Promise<LoadedIcon | null> => {
    try {
      const url = await invoke<string>("read_icon", { filename });
      const image = await decode(url);
      return { url, color: dominantColor(image) };
    } catch {
      return null;
    }
  })();

  cache.set(filename, task);
  return task;
}

/** Oublie une Icône du cache, après un remplacement ou une suppression. */
export function forgetIcon(filename: string): void {
  cache.delete(filename);
}

function decode(url: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const image = new Image();
    image.onload = () => resolve(image);
    image.onerror = () => reject(new Error("image illisible"));
    image.src = url;
  });
}

/**
 * Couleur dominante : image réduite à 64x64, pixels opaques uniquement,
 * quantification par median cut en 8 couleurs, puis assombrissement (IC-15).
 */
export function dominantColor(image: HTMLImageElement): string {
  const size = 64;
  const canvas = document.createElement("canvas");
  canvas.width = size;
  canvas.height = size;
  const ctx = canvas.getContext("2d", { willReadFrequently: true });
  if (!ctx) return TILE_DEFAULT;

  ctx.drawImage(image, 0, 0, size, size);
  const { data } = ctx.getImageData(0, 0, size, size);

  const opaque: RGB[] = [];
  for (let i = 0; i < data.length; i += 4) {
    if (data[i + 3] >= 128) opaque.push([data[i], data[i + 1], data[i + 2]]);
  }
  if (opaque.length === 0) return TILE_DEFAULT;

  const [r, g, b] = darken(largestBucketAverage(medianCut(opaque, 8)));
  return `#${hex(r)}${hex(g)}${hex(b)}`;
}

type RGB = [number, number, number];

/** Découpe récursive du nuage de pixels en `count` boîtes (median cut). */
function medianCut(pixels: RGB[], count: number): RGB[][] {
  let buckets: RGB[][] = [pixels];
  while (buckets.length < count) {
    const index = widestBucket(buckets);
    if (index < 0) break;
    const bucket = buckets[index];
    const channel = widestChannel(bucket);
    const sorted = [...bucket].sort((a, b) => a[channel] - b[channel]);
    const middle = sorted.length >> 1;
    buckets = [
      ...buckets.slice(0, index),
      sorted.slice(0, middle),
      sorted.slice(middle),
      ...buckets.slice(index + 1),
    ].filter((b) => b.length > 0);
  }
  return buckets;
}

function widestBucket(buckets: RGB[][]): number {
  let best = -1;
  let bestSpread = 0;
  buckets.forEach((bucket, index) => {
    if (bucket.length < 2) return;
    const spread = channelSpread(bucket, widestChannel(bucket));
    if (spread >= bestSpread) {
      bestSpread = spread;
      best = index;
    }
  });
  return best;
}

function widestChannel(bucket: RGB[]): 0 | 1 | 2 {
  const spreads = [channelSpread(bucket, 0), channelSpread(bucket, 1), channelSpread(bucket, 2)];
  const max = Math.max(...spreads);
  return spreads.indexOf(max) as 0 | 1 | 2;
}

function channelSpread(bucket: RGB[], channel: 0 | 1 | 2): number {
  let min = 255;
  let max = 0;
  for (const pixel of bucket) {
    if (pixel[channel] < min) min = pixel[channel];
    if (pixel[channel] > max) max = pixel[channel];
  }
  return max - min;
}

/** Moyenne de la boîte qui contient le plus de pixels. */
function largestBucketAverage(buckets: RGB[][]): RGB {
  let best = buckets[0];
  for (const bucket of buckets) {
    if (bucket.length > best.length) best = bucket;
  }
  const sum = best.reduce<RGB>(
    (acc, [r, g, b]) => [acc[0] + r, acc[1] + g, acc[2] + b],
    [0, 0, 0],
  );
  return [
    Math.round(sum[0] / best.length),
    Math.round(sum[1] / best.length),
    Math.round(sum[2] / best.length),
  ];
}

/** Assombrissement, avec un second passage si la couleur reste claire (IC-15). */
function darken([r, g, b]: RGB): RGB {
  let out: RGB = [Math.round(r * 0.6), Math.round(g * 0.6), Math.round(b * 0.6)];
  const luminance = 0.299 * out[0] + 0.587 * out[1] + 0.114 * out[2];
  if (luminance > 140) {
    out = [Math.round(out[0] * 0.6), Math.round(out[1] * 0.6), Math.round(out[2] * 0.6)];
  }
  return out;
}

function hex(value: number): string {
  return Math.max(0, Math.min(255, value)).toString(16).padStart(2, "0");
}
