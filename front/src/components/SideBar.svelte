<script lang="ts">
    import { Button } from "$lib/components/ui/button";

    import { createEventDispatcher } from 'svelte';

    export let sidebar_shown: boolean = false
    
    const dispatch = createEventDispatcher<{changeApp: string}>();

    function changeApp(app: string) {
        dispatch('changeApp', app);
    }

</script>

<main class="border-r-[1px] border-b-[1px] border-[#47003C] w-40 z-10 bg-[#150013] text-center py-4 flex-grow-0 flex-shrink-0 {sidebar_shown ? "" : "hidden"}">
    <Button class="w-32 mb-2" on:click={() => {changeApp("home");window.history.pushState("", "", '/');}}>Home</Button>
    <Button class="w-32 mb-2" on:click={() => {changeApp("twitch");window.history.pushState("", "", '/twitch');}}>Twitch</Button>
    <Button class="w-32 mb-2" on:click={() => {changeApp("roles");window.history.pushState("", "", '/roles');}}>Roles</Button>
</main>

<style>
    @media (min-width: 600px) {
        main {
            display: block;
        }
    }
    @media (max-width: 600px) {
        main {
            position: fixed;
        }
    }

</style>
