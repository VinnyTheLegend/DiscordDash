<script lang="ts">
    import { fetch_guild, role_colors } from "../../../utils";
    import { onMount } from "svelte";
    import { guild_info } from "../../../stores";
  import { RotateCounterClockwise } from "svelte-radix";

    export let USER: User;

    interface RoleWithColor extends Role {
        color: string
    }
    let roles_with_color: RoleWithColor[] = []

    let guild_info_value: GuildInfo
    guild_info.subscribe((value) => {
        guild_info_value = value
        if (value && USER.roles) {
            console.log(USER.roles)
            for (let i in value.roles) {
                for (let k=0; k < USER.roles.length; k++) {
                    if (value.roles[i].id === USER.roles[k] && value.roles[i].name in role_colors) {                    
                        roles_with_color.push({...value.roles[i], color: role_colors[value.roles[i].name].color})
                    }
                }
            }
            roles_with_color = roles_with_color
        }
    })

    $: if(USER.roles) {
        if (guild_info_value && USER.roles) {
            roles_with_color = []
            console.log(USER.roles)
            for (let i in guild_info_value.roles) {
                for (let k=0; k < USER.roles.length; k++) {
                    if (guild_info_value.roles[i].id === USER.roles[k] && guild_info_value.roles[i].name in role_colors) {                    
                        roles_with_color.push({...guild_info_value.roles[i], color: role_colors[guild_info_value.roles[i].name].color})
                    }
                }
            }
            roles_with_color = roles_with_color
        }
    }

    onMount(() => {
        if (typeof guild_info_value === 'undefined') {
            fetch_guild()
        }
    })

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
    {#if USER.connection_time > 60}
        <div class="flex">
            <h1 class="w-5/12 px-1">Connection Time:</h1><h1 class="w-7/12 text-right px-1">{(USER.connection_time/60).toFixed(1)}hrs</h1>
        </div>
    {:else}
        <div class="flex">
            <h1 class="w-5/12 px-1">Connection Time:</h1><h1 class="w-7/12 text-right px-1">{USER.connection_time.toFixed(1)}mins</h1>
        </div>
    {/if}
    {#if USER.muted_time > 60}
        <div class="flex">
            <h1 class="w-5/12 px-1">Muted Time:</h1><h1 class="w-7/12 text-right px-1">{(USER.muted_time/60).toFixed(1)}hrs</h1>
        </div>
    {:else}
        <div class="flex">
            <h1 class="w-5/12 px-1">Muted Time:</h1><h1 class="w-7/12 text-right px-1">{USER.muted_time.toFixed(1)}mins</h1>
        </div>
    {/if}
    {#if USER.deafened_time > 60}
        <div class="flex">
            <h1 class="w-5/12 px-1">Deafened Time:</h1><h1 class="w-7/12 text-right px-1">{(USER.deafened_time/60).toFixed(1)}hrs</h1>
        </div>
    {:else}
        <div class="flex">
            <h1 class="w-5/12 px-1">Deafened Time:</h1><h1 class="w-7/12 text-right px-1">{USER.deafened_time.toFixed(1)}mins</h1>
        </div>
    {/if}
    {#if roles_with_color}      
        <div class="border-t border-border grow flex flex-col">
            <div class="flex flex-wrap justify-evenly px-2">
                {#each roles_with_color as role (role)}
                        <div style="background-color: {role_colors[role.name].color}" class="my-2 h-fit p-1.5 rounded-2xl border border-border">{role.name}</div>
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
