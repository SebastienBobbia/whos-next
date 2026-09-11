import type { Page } from "@playwright/test";
import type { Member } from "../src/lib/types";

/** Équipe utilisée par les tests : Yoann est Absent du dernier daily. */
export const TEAM: Member[] = [
  { name: "Adeline", icon_type: "", icon_value: "" },
  { name: "Camille", icon_type: "emoji", icon_value: "🦄" },
  { name: "Marion", icon_type: "", icon_value: "" },
  { name: "Yoann", icon_type: "", icon_value: "", absent: true },
];

/**
 * Installe un faux IPC Tauri avant le chargement de l'application.
 *
 * `@tauri-apps/api` appelle `window.__TAURI_INTERNALS__.invoke(cmd, args)`.
 * Le bouchon garde l'Équipe en mémoire et enregistre tous les appels dans
 * `window.__CALLS__`, que les tests inspectent.
 */
export async function installTauriMock(page: Page, team: Member[] = TEAM): Promise<void> {
  await page.addInitScript((initialTeam: Member[]) => {
    const calls: { cmd: string; args: unknown }[] = [];
    let members: Member[] = JSON.parse(JSON.stringify(initialTeam));

    // 1 pixel transparent, suffisant pour les Icônes image.
    const PIXEL =
      "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII=";

    async function invoke(cmd: string, args: Record<string, unknown> = {}) {
      calls.push({ cmd, args });
      switch (cmd) {
        case "load_team":
          return JSON.parse(JSON.stringify(members));
        case "save_team":
          members = JSON.parse(JSON.stringify(args.members));
          return null;
        case "import_icon":
          return String(args.source).split(/[\\/]/).pop();
        case "read_icon":
          return PIXEL;
        case "remove_icon":
        case "restore_window":
        case "set_always_on_top":
        case "quit_app":
          return null;
        case "fit_to_right_edge":
          return { width: 260, height: 900 };
        case "monitor_work_area":
          return { x: 0, y: 0, width: 1920, height: 1040, scale: 1 };
        case "plugin:dialog|open":
          return "C:\\images\\photo.png";
        default:
          return null;
      }
    }

    Object.defineProperty(window, "__TAURI_INTERNALS__", {
      value: {
        invoke,
        transformCallback: (callback: unknown) => callback,
        unregisterCallback: () => {},
        convertFileSrc: (path: string) => path,
      },
      writable: false,
    });

    Object.defineProperty(window, "__CALLS__", { value: calls, writable: false });
    Object.defineProperty(window, "__MEMBERS__", {
      get: () => members,
      configurable: true,
    });
  }, team);
}

/** Commandes enregistrées par le bouchon, dans l'ordre d'appel. */
export function calls(page: Page): Promise<{ cmd: string; args: any }[]> {
  return page.evaluate(() => (window as any).__CALLS__.map((c: any) => ({ ...c })));
}

/** État de l'Équipe dans le bouchon, après les sauvegardes. */
export function storedMembers(page: Page): Promise<Member[]> {
  return page.evaluate(() => JSON.parse(JSON.stringify((window as any).__MEMBERS__)));
}
