<script lang="ts">
    import { Button } from "$lib/components/ui/button";

    import { createEventDispatcher } from 'svelte';

    
    const dispatch = createEventDispatcher<{changeApp: string}>();

    function changeApp(app: string) {
        dispatch('changeApp', app);
    }

</script>

<main class="border-r-[1px] border-[#47003C] w-40 bg-[#150013] text-center py-4">
    <Button class="w-32" on:click={() => {changeApp("test")}}>Test</Button>
</main>

<style>

</style>
