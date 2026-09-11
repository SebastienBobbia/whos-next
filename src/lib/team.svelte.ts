/**
 * État de l'Équipe : chargement, modifications et sauvegarde.
 *
 * Chaque modification écrit team.json tout de suite (PE-08). Les identifiants
 * EQ-xx, IC-xx et PR-xx renvoient à docs/spec/.
 */
import { invoke } from "@tauri-apps/api/core";
import { forgetIcon } from "./icons";
import { sameName, type IconType, type Member } from "./types";

class TeamStore {
  members = $state<Member[]>([]);

  async load(): Promise<void> {
    this.members = await invoke<Member[]>("load_team");
  }

  private async persist(): Promise<void> {
    await invoke("save_team", { members: $state.snapshot(this.members) });
  }

  private find(name: string): Member | undefined {
    return this.members.find((m) => m.name === name);
  }

  /** Ajoute un Membre à la fin de l'Équipe (EQ-08). */
  async add(rawName: string): Promise<{ ok: true } | { ok: false; error: string }> {
    const name = rawName.trim();
    if (!name) return { ok: false, error: "Veuillez entrer un nom." };
    if (this.members.some((m) => sameName(m.name, name))) {
      return { ok: false, error: `"${name}" existe déjà dans l'équipe.` };
    }
    this.members.push({ name, icon_type: "", icon_value: "" });
    await this.persist();
    return { ok: true };
  }

  /** Supprime un Membre et le fichier de son Icône image (EQ-12). */
  async remove(name: string): Promise<void> {
    const member = this.find(name);
    if (!member) return;
    this.members = this.members.filter((m) => m.name !== name);
    await this.persist();
    if (member.icon_type === "image" && member.icon_value) {
      forgetIcon(member.icon_value);
      await invoke("remove_icon", { filename: member.icon_value });
    }
  }

  /** Déplace un Membre : `to` est la position d'insertion avant déplacement (EQ-13). */
  async reorder(from: number, to: number): Promise<void> {
    if (from === to || from === to - 1) return;
    const next = [...this.members];
    const [moved] = next.splice(from, 1);
    next.splice(to > from ? to - 1 : to, 0, moved);
    this.members = next;
    await this.persist();
  }

  /**
   * Définit l'Icône d'un Membre. Une image est copiée dans icons\ avant que
   * l'ancienne ne soit supprimée (IC-07, IC-11, IC-12).
   *
   * @param source pour une image : chemin absolu du fichier choisi.
   */
  async setIcon(name: string, iconType: IconType, source: string): Promise<void> {
    const member = this.find(name);
    if (!member) return;
    const previous =
      member.icon_type === "image" && member.icon_value ? member.icon_value : null;

    if (iconType === "image") {
      const filename = await invoke<string>("import_icon", { source });
      member.icon_type = "image";
      member.icon_value = filename;
    } else {
      member.icon_type = iconType;
      member.icon_value = iconType === "emoji" ? source : "";
    }

    await this.persist();

    if (previous && previous !== member.icon_value) {
      forgetIcon(previous);
      await invoke("remove_icon", { filename: previous });
    }
  }

  /** Enregistre les Absents au lancement d'une Session (PR-09). */
  async saveAbsents(presentNames: string[]): Promise<void> {
    const present = new Set(presentNames);
    for (const member of this.members) {
      if (present.has(member.name)) delete member.absent;
      else member.absent = true;
    }
    await this.persist();
  }
}

export const team = new TeamStore();
