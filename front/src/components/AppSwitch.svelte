<script lang="ts">
    import Home from "./apps/home/Home.svelte";
  import LeftOrRight from "./apps/leftorright/LeftOrRight.svelte";
  import RolesComp from "./apps/roles/RolesComp.svelte";
    import Twitch from "./apps/twitch/Twitch.svelte";

    export let USER: User
    export let current_app: string
</script>

<main class="flex size-full min-w-0">
{#if current_app === "home"}
    <Home {USER}/>
{:else if current_app === "twitch"}
    <Twitch />
{:else if current_app === "roles"}
    <RolesComp />
{:else if current_app === "leftorright"}
    <LeftOrRight />
{/if}
</main>

<style>

</style>
