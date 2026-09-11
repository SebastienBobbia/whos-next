<script lang="ts">
  // Squelette de navigation. Les trois vues arrivent dans les commits suivants.
  type View = "equipe" | "presence" | "session";

  let view = $state<View>("equipe");
</script>

<main>
  <p>Vue courante : {view}</p>
</main>

<style>
  main {
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 14px;
    color: var(--txt-dim);
  }
</style>
