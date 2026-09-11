<script lang="ts">
  import { invoke } from "@tauri-apps/api/core";
  import Glyph from "./lib/Glyph.svelte";
  import { team } from "./lib/team.svelte";
  import type { Member } from "./lib/types";
  import Equipe from "./views/Equipe.svelte";
  import IconPicker from "./views/IconPicker.svelte";
  import Presence from "./views/Presence.svelte";
  import Session from "./views/Session.svelte";

  /** Taille des vues Équipe et Présence, en pixels logiques (FE-03). */
  const FORM_WIDTH = 420;
  const FORM_HEIGHT = 550;

  type View = "equipe" | "presence" | "session";

  let view = $state<View>("equipe");
  let attendees = $state<string[]>([]);
  let editing = $state<Member | null>(null);
  let onTop = $state(true);
  let ready = $state(false);

  $effect(() => {
    team.load().then(() => (ready = true));
  });

  async function toForm(next: View) {
    view = next;
    await invoke("restore_window", { width: FORM_WIDTH, height: FORM_HEIGHT });
  }

  function startSession(present: string[]) {
    attendees = present;
    view = "session";
  }

  async function toggleOnTop() {
    onTop = !onTop;
    await invoke("set_always_on_top", { onTop });
  }
</script>

{#if ready}
  {#if view === "session"}
    <Session {attendees} onEnd={() => toForm("equipe")} />
  {:else}
    <div class="shell">
      {#if view === "equipe"}
        <Equipe onPrepare={() => (view = "presence")} onEditIcon={(m) => (editing = m)} />
      {:else}
        <Presence onBack={() => (view = "equipe")} onStart={startSession} />
      {/if}

      <button class="ontop" onclick={toggleOnTop}>
        <span class="box" class:on={onTop}>
          {#if onTop}<Glyph name="check" size={12} stroke={3} />{/if}
        </span>
        Toujours au premier plan
      </button>
    </div>

    {#if editing}
      <IconPicker member={editing} onClose={() => (editing = null)} />
    {/if}
  {/if}
{/if}

<style>
  .shell {
    height: 100%;
    display: flex;
    flex-direction: column;
  }

  .ontop {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 6px;
    padding: 8px 0 10px;
    border: 0;
    background: transparent;
    font: inherit;
    font-size: 11px;
    color: var(--txt-dim);
    cursor: pointer;
  }

  .box {
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid var(--ink-line);
    background: var(--ink-field);
    display: flex;
    align-items: center;
    justify-content: center;
    color: #fff;
  }

  .box.on {
    background: var(--blue);
    border-color: transparent;
  }
</style>
