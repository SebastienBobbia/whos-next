/** Un Membre de l'Équipe, tel qu'il est stocké dans team.json (voir docs/spec/06-persistance.md). */
export type Member = {
  name: string;
  /** "emoji" | "image" | "" (pas d'Icône) */
  icon_type: IconType;
  /** caractère emoji, nom de fichier dans icons\, ou "" */
  icon_value: string;
  /** Absent : présent uniquement quand il vaut true */
  absent?: boolean;
};

export type IconType = "" | "emoji" | "image";

/** Compare deux noms de Membre : casse ignorée, accents distincts (EQ-10). */
export function sameName(a: string, b: string): boolean {
  return a.trim().toLocaleLowerCase("fr") === b.trim().toLocaleLowerCase("fr");
}
