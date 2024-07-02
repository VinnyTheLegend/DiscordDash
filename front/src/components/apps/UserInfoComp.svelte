<script lang="ts">
    import { ROLES_DICT } from "../../utils";

    export let USER: User;

</script>

<main class="flex flex-col w-[325px] h-[500px] border-2 border-border rounded bg-background">
    <div class="flex">
        <h1 class="w-1/3 px-1">Username:</h1><h1 class="w-2/3 text-right px-1">{USER.username}</h1>
    </div>
    <div class="flex">
        <h1 class="w-1/3 px-1">Global Name:</h1><h1 class="w-2/3 text-right px-1">{USER.global_name}</h1>
    </div>
    <div class="flex">
        <h1 class="w-1/3 px-1">Nickname:</h1><h1 class="w-2/3 text-right px-1">{USER.nickname}</h1>
    </div>
    {#if USER.joined_at}   
        <div class="flex">
            <h1 class="w-1/3 px-1">Join Date:</h1><h1 class="w-2/3 text-right px-1">{(() => new Date(USER.joined_at).toDateString())()}</h1>
        </div>
    {/if}
    <div class="flex">
        <h1 class="w-1/3 px-1">Test</h1><h1 class="w-2/3 text-right px-1">Test</h1>
    </div>
    {#if USER.roles}      
        <div class="border-t border-border grow flex flex-col">
            <h1 class="text-center text-xl">Roles</h1>
            <div class="flex flex-wrap grow justify-evenly p-2">
                {#each USER.roles as role}
                    {#if ROLES_DICT[role].name != "Everyone"}
                        <div class="bg-[{ROLES_DICT[role].color}] h-fit p-1.5 rounded-2xl border border-border">{ROLES_DICT[role].name}</div>
                    {/if}
                {/each}
            </div>
        </div>
    {/if}
</main>

<style>
h1 {
    text-shadow: -1px -1px 0 #47003C, 1px -1px 0 #47003C, -1px 1px 0 #47003C, 1px 1px 0 #47003C;
}
</style>
