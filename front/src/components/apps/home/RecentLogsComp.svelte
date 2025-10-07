<script lang="ts">
import { URLS } from "../../../utils";
import { onMount } from 'svelte';


let recent_logs: string[] = []
export let visible = false
$: if (visible) {
  fetch(URLS.BASE_URL+'/api/logs/recent', { mode: "cors", credentials: "include" })
      .then((response) => {
        if (response.status === 400) {
          return response.json().then((data) => {
            throw new Error(data.detail || "Bad request");
          });
        }
        return response.json();
      })
      .then((data: string[]) => {
          recent_logs = data
      })
      .catch((error) => {
          console.log(error);
      });
}

</script>

<main class="h-[500px] border-2 border-border rounded bg-background">
    <ol class="h-full flex flex-col-reverse overflow-y-auto overflow-x-hidden">
        {#each [...recent_logs].reverse() as log}
            <li class="px-1 text-nowrap">{log}</li>
        {/each}
    </ol>
</main>

<style>
  @media(max-width:790px) {
  main {
      width: 400px;
  }
  ol {
    overflow-x: auto
  }
  }
  * {
    box-sizing: border-box;
}
</style>
