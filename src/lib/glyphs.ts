/**
 * Pictogrammes de l'interface, dessinés en SVG sur une grille de 24 px.
 * Chaque valeur est le contenu d'un <svg viewBox="0 0 24 24">.
 */
export const GLYPHS = {
  fit: '<path d="M3 12h18"/><path d="M7 8l-4 4 4 4"/><path d="M17 8l4 4-4 4"/>',
  draw:
    '<rect x="4" y="4" width="16" height="16" rx="3"/>' +
    '<circle cx="9" cy="9" r="1.1" fill="currentColor"/><circle cx="15" cy="9" r="1.1" fill="currentColor"/>' +
    '<circle cx="9" cy="15" r="1.1" fill="currentColor"/><circle cx="15" cy="15" r="1.1" fill="currentColor"/>',
  undo: '<path d="M9 14L4 9l5-5"/><path d="M4 9h10a6 6 0 0 1 0 12h-3"/>',
  stop: '<rect x="6" y="6" width="12" height="12" rx="1.5"/>',
  handle:
    '<circle cx="9" cy="6" r="1" fill="currentColor"/><circle cx="9" cy="12" r="1" fill="currentColor"/>' +
    '<circle cx="9" cy="18" r="1" fill="currentColor"/><circle cx="15" cy="6" r="1" fill="currentColor"/>' +
    '<circle cx="15" cy="12" r="1" fill="currentColor"/><circle cx="15" cy="18" r="1" fill="currentColor"/>',
  close: '<path d="M6 6l12 12"/><path d="M18 6L6 18"/>',
  image: '<rect x="3" y="5" width="18" height="14" rx="2"/><circle cx="9" cy="10" r="1.5"/><path d="M21 16l-5-5-8 8"/>',
  plus: '<path d="M12 5v14"/><path d="M5 12h14"/>',
  check: '<path d="M5 12l5 5 9-10"/>',
  back: '<path d="M19 12H5"/><path d="M11 6l-6 6 6 6"/>',
  go: '<path d="M5 12h14"/><path d="M13 6l6 6-6 6"/>',
} as const;

export type GlyphName = keyof typeof GLYPHS;
