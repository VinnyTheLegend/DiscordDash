<script lang="ts">
    import Home from "./apps/home/Home.svelte";
  import LeftOrRight from "./apps/leftorright/LeftOrRight.svelte";
  import RolesComp from "./apps/roles/RolesComp.svelte";
    import Twitch from "./apps/twitch/Twitch.svelte";

    export let USER: User
    export let current_app: string
</script>

<div class="w-full flex-grow">
    <div class="size-full" style:display={current_app === 'home' ? 'block' : 'none'}>
        <Home {USER} visible={current_app === 'home'}/>
    </div>
    <div class="size-full" style:display={current_app === 'twitch' ? 'block' : 'none'}>
        <Twitch visible={current_app === 'twitch'} />
    </div>
    <div class="size-full" style:display={current_app === 'roles' ? 'block' : 'none'}>
        <RolesComp visible={current_app === 'roles'}/>
    </div>
    <div class="size-full" style:display={current_app === 'leftorright' ? 'block' : 'none'}>
        <LeftOrRight visible={current_app === 'leftorright'} />
    </div>
</div>

<style>

</style>
