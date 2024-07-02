<script lang="ts">
import { URLS } from "../../../utils";

let recent_logs: string[]

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
            return [];
        });

</script>

<main class="w-[650px] h-[500px] border-2 border-border rounded bg-background">
    {#if recent_logs}
        <ol class="size-full overflow-auto p-1 flex flex-col-reverse">
            {#each recent_logs.reverse() as log}
                <li class="text-nowrap">{log}</li>
            {/each}
        </ol>
    {/if}

</main>

<style>

</style>
