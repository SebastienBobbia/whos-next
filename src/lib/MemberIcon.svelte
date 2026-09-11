<script lang="ts">
  import { loadIcon } from "./icons";
  import type { Member } from "./types";

  let { member, size = 24 }: { member: Member; size?: number } = $props();

  // L'Icône image est lue une seule fois puis servie par le cache (PF-11).
  let url = $state<string | null>(null);

  $effect(() => {
    const { icon_type, icon_value } = member;
    if (icon_type !== "image" || !icon_value) {
      url = null;
      return;
    }
    let cancelled = false;
    loadIcon(icon_value).then((icon) => {
      if (!cancelled) url = icon?.url ?? null;
    });
    return () => {
      cancelled = true;
    };
  });
</script>

{#if member.icon_type === "emoji" && member.icon_value}
  <span class="emoji" style="font-size: {size - 4}px; width: {size}px">{member.icon_value}</span>
{:else if url}
  <img src={url} alt="" width={size} height={size} />
{/if}

<style>
  .emoji {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
    flex-shrink: 0;
  }

  img {
    object-fit: contain;
    flex-shrink: 0;
  }
</style>
