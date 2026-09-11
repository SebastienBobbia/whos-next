<script lang="ts">
  import Glyph from "../lib/Glyph.svelte";
  import MemberIcon from "../lib/MemberIcon.svelte";
  import { team } from "../lib/team.svelte";

  let { onBack, onStart }: { onBack: () => void; onStart: (attendees: string[]) => void } =
    $props();

  // Coché par défaut, sauf pour les Absents du dernier daily (PR-04).
  let checked = $state<Record<string, boolean>>(
    Object.fromEntries(team.members.map((m) => [m.name, !m.absent])),
  );

  const present = $derived(team.members.filter((m) => checked[m.name]).map((m) => m.name));

  function setAll(value: boolean) {
    checked = Object.fromEntries(team.members.map((m) => [m.name, value]));
  }

  async function start() {
    if (present.length === 0) return;
    await team.saveAbsents(present);
    onStart(present);
  }
</script>

<div class="view">
  <header>
    <h1>Qui est présent ?</h1>
    <p>Cochez les personnes présentes au daily</p>
  </header>

  <div class="toggles">
    <button class="toggle on" onclick={() => setAll(true)}>Tout cocher</button>
    <button class="toggle" onclick={() => setAll(false)}>Tout décocher</button>
  </div>

  <ul class="list">
    {#each team.members as member (member.name)}
      <li class="row" class:off={!checked[member.name]}>
        <label>
          <input type="checkbox" bind:checked={checked[member.name]} />
          <span class="box" aria-hidden="true">
            {#if checked[member.name]}<Glyph name="check" size={13} stroke={3} />{/if}
          </span>
          <MemberIcon {member} size={22} />
          <span class="name">{member.name}</span>
        </label>
      </li>
    {/each}
  </ul>

  <p class="count">{present.length}/{team.members.length} présents</p>

  <div class="actions">
    <button class="back" onclick={onBack}><Glyph name="back" size={14} /> Retour</button>
    <button class="cta" onclick={start} disabled={present.length === 0}>
      Démarrer le Daily <Glyph name="go" />
    </button>
  </div>
</div>

<style>
  .view {
    height: 100%;
    display: flex;
    flex-direction: column;
    gap: 10px;
    padding: 18px 20px 0;
  }

  header {
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 2px;
  }

  h1 {
    margin: 0;
    font-size: 20px;
    font-weight: 800;
  }

  header p {
    margin: 0;
    font-size: 12px;
    color: var(--txt-dim);
  }

  button {
    border: 0;
    border-radius: 6px;
    font: inherit;
    color: var(--txt);
    cursor: pointer;
  }

  .toggles {
    display: flex;
    gap: 8px;
  }

  .toggle {
    flex: 1 1 0;
    height: 30px;
    font-size: 12px;
    font-weight: 600;
    background: var(--ink-field);
    border: 1px solid var(--ink-line);
    color: var(--txt-dim);
  }

  .toggle.on {
    background: #2a2a4d;
    border-color: transparent;
    color: var(--txt);
  }

  .list {
    flex: 1 1 0;
    min-height: 0;
    overflow-y: auto;
    margin: 0;
    padding: 0;
    list-style: none;
    display: flex;
    flex-direction: column;
    gap: 4px;
  }

  .row {
    height: 38px;
    flex-shrink: 0;
    border-radius: 8px;
    background: var(--ink-row);
  }

  .row.off {
    background: #1c1c34;
  }

  label {
    height: 100%;
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 0 10px;
    cursor: pointer;
  }

  input {
    position: absolute;
    opacity: 0;
    pointer-events: none;
  }

  .box {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    border-radius: 5px;
    border: 1px solid var(--ink-line);
    background: var(--ink-field);
    display: flex;
    align-items: center;
    justify-content: center;
  }

  input:checked + .box {
    background: var(--blue);
    border-color: transparent;
    color: #fff;
  }

  .name {
    flex-grow: 1;
    font-size: 14px;
    font-weight: 500;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .row.off .name {
    color: var(--txt-faint);
  }

  .count {
    margin: 0;
    text-align: center;
    font-size: 12px;
    color: var(--txt-dim);
  }

  .actions {
    display: flex;
    gap: 8px;
    margin-bottom: 4px;
  }

  .back {
    width: 96px;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    background: var(--ink-field);
    border: 1px solid var(--ink-line);
    font-size: 13px;
    font-weight: 600;
    color: var(--txt-dim);
  }

  .cta {
    flex-grow: 1;
    height: 40px;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    background: var(--blue);
    font-size: 14px;
    font-weight: 800;
  }

  .cta:disabled {
    opacity: 0.5;
    cursor: default;
  }
</style>
