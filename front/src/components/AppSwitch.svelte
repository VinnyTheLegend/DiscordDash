<script lang="ts">

    export let current_app: string
</script>

<main class="flex flex-grow">
{#if current_app === "home"}
    <div class="size-full border-2 border-red-500">

    </div>
{:else if current_app === "test"}
    <div class="size-full border-2 border-green-500">

    </div>
{/if}
</main>

<style>

</style>
