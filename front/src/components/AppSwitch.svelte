<script lang="ts">
    import Home from "./apps/home/Home.svelte";
    import Twitch from "./apps/twitch/Twitch.svelte";

    export let USER: User
    export let current_app: string
</script>

<main class="flex size-full min-w-0">
{#if current_app === "home"}
    <Home {USER}/>
{:else if current_app === "twitch"}
    <Twitch />
{/if}
</main>

<style>

</style>
