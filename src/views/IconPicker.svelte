<script lang="ts">
  import { open } from "@tauri-apps/plugin-dialog";
  import { untrack } from "svelte";
  import { EMOJI_GRID } from "../lib/emojis";
  import { team } from "../lib/team.svelte";
  import type { Member } from "../lib/types";

  let { member, onClose }: { member: Member; onClose: () => void } = $props();

  // Pré-sélection depuis l'Icône actuelle, figée à l'ouverture (IC-03).
  let emoji = $state<string | null>(
    untrack(() => (member.icon_type === "emoji" ? member.icon_value : null)),
  );
  // Chemin absolu d'une image fraîchement choisie. L'Icône image actuelle n'en est pas une :
  // valider sans rien changer ne doit rien modifier (IC-07).
  let file = $state<string | null>(null);

  const fileLabel = $derived(
    file ? shorten(file) : member.icon_type === "image" ? member.icon_value : "Aucun fichier",
  );

  function shorten(path: string): string {
    const name = path.split(/[\\/]/).pop() ?? path;
    return name.length > 28 ? `${name.slice(0, 25)}…` : name;
  }

  function pickEmoji(value: string) {
    emoji = emoji === value ? null : value;
    file = null;
  }

  async function browse() {
    const chosen = await open({
      title: "Choisir une image",
      multiple: false,
      directory: false,
      filters: [
        { name: "Images", extensions: ["png", "jpg", "jpeg", "gif", "bmp", "webp", "svg"] },
        { name: "Tous les fichiers", extensions: ["*"] },
      ],
    });
    if (typeof chosen === "string") {
      file = chosen;
      emoji = null;
    }
  }

  async function clearIcon() {
    await team.setIcon(member.name, "", "");
    onClose();
  }

  async function confirm() {
    if (file) await team.setIcon(member.name, "image", file);
    else if (emoji) await team.setIcon(member.name, "emoji", emoji);
    onClose();
  }
</script>

<div
  class="backdrop"
  role="button"
  tabindex="-1"
  onclick={onClose}
  onkeydown={(e) => e.key === "Escape" && onClose()}>
</div>

<div class="dialog" role="dialog" aria-label="Choix d'icône">
  <header>
    <h2>Icône — {member.name}</h2>
    <p>Choisissez un emoji ou importez une image</p>
  </header>

  <div class="grid">
    {#each EMOJI_GRID as value (value)}
      <button class="cell" class:selected={emoji === value} onclick={() => pickEmoji(value)}>
        {value}
      </button>
    {/each}
  </div>

  <div class="file">
    <div class="file-text">
      <span class="file-title">Image personnalisée</span>
      <span class="file-name">{fileLabel}</span>
    </div>
    <button class="browse" onclick={browse}>Parcourir…</button>
  </div>

  <footer>
    <button class="danger" onclick={clearIcon}>Supprimer l'icône</button>
    <span class="spacer"></span>
    <button class="ghost" onclick={onClose}>Annuler</button>
    <button class="primary" onclick={confirm}>Valider</button>
  </footer>
</div>

<style>
  .backdrop {
    position: fixed;
    inset: 0;
    background: rgba(8, 8, 18, 0.7);
    border: 0;
  }

  .dialog {
    position: fixed;
    inset: 12px;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 16px;
    border-radius: 12px;
    background: var(--ink);
    box-shadow: 0 18px 40px rgba(0, 0, 0, 0.5);
    overflow-y: auto;
  }

  h2 {
    margin: 0;
    font-size: 17px;
    font-weight: 800;
  }

  header p {
    margin: 2px 0 0;
    font-size: 12px;
    color: var(--txt-dim);
  }

  button {
    border: 0;
    border-radius: 8px;
    font: inherit;
    color: var(--txt);
    cursor: pointer;
  }

  .grid {
    display: grid;
    grid-template-columns: repeat(8, minmax(0, 1fr));
    gap: 6px;
  }

  .cell {
    aspect-ratio: 1;
    background: var(--ink-row);
    font-size: 18px;
    line-height: 1;
  }

  .cell.selected {
    background: #1a5c2a;
    outline: 2px solid #4ade80;
    outline-offset: -2px;
  }

  .file {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 10px 12px;
    border-radius: 8px;
    background: var(--ink-row);
  }

  .file-text {
    flex-grow: 1;
    display: flex;
    flex-direction: column;
    gap: 2px;
    min-width: 0;
  }

  .file-title {
    font-size: 12px;
    font-weight: 600;
  }

  .file-name {
    font-size: 11px;
    color: var(--txt-dim);
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .browse {
    height: 30px;
    padding: 0 12px;
    background: #30305a;
    font-size: 12px;
    font-weight: 600;
  }

  footer {
    margin-top: auto;
    display: flex;
    align-items: center;
    gap: 8px;
  }

  .spacer {
    flex-grow: 1;
  }

  .danger {
    height: 34px;
    padding: 0 12px;
    background: var(--red);
    color: var(--red-txt);
    font-size: 12px;
    font-weight: 600;
  }

  .ghost {
    width: 80px;
    height: 34px;
    background: var(--ink-field);
    border: 1px solid var(--ink-line);
    color: var(--txt-dim);
    font-size: 13px;
    font-weight: 600;
  }

  .primary {
    width: 80px;
    height: 34px;
    background: var(--blue);
    font-size: 13px;
    font-weight: 700;
  }
</style>
