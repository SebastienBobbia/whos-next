<script lang="ts">
  import { GLYPHS, type GlyphName } from "./glyphs";

  let { name, size = 16, stroke = 2 }: { name: GlyphName; size?: number; stroke?: number } =
    $props();
</script>

<svg
  width={size}
  height={size}
  viewBox="0 0 24 24"
  fill="none"
  stroke="currentColor"
  stroke-width={stroke}
  stroke-linecap="round"
  stroke-linejoin="round"
  aria-hidden="true">{@html GLYPHS[name]}</svg
>
