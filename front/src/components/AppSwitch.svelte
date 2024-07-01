<script lang="ts">
    import Home from "./apps/home/Home.svelte";

    export let USER: User
    export let current_app: string
</script>

<main class="flex flex-grow">
{#if current_app === "home"}
    <Home {USER}/>
{:else if current_app === "test"}
    <div class="size-full border-2 border-green-500">

    </div>
{/if}
</main>

<style>

</style>
