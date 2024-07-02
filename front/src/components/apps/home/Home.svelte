<script lang="ts">
    import UserInfoComp from "./UserInfoComp.svelte";
    import GuildInfoComp from "./GuildInfoComp.svelte";
    import RecentLogsComp from "./RecentLogsComp.svelte";

    export let USER: User;

</script>

<main class="size-full flex justify-evenly items-center">
    <div class="">
        <h1 class="text-center font-extrabold text-xl">Server</h1>
        <GuildInfoComp/>
    </div>
    <div>
        <h1 class="text-center font-extrabold text-xl">Recent Logs</h1>    
        <RecentLogsComp/>
    </div>
    <div>
        <h1 class="text-center font-extrabold text-xl">{USER?.username || "User"}</h1>
        <UserInfoComp {USER}/>
    </div>
</main>

<style>
h1 {
    text-shadow: -1px -1px 0 #47003C, 1px -1px 0 #47003C, -1px 1px 0 #47003C, 1px 1px 0 #47003C;
}
</style>
