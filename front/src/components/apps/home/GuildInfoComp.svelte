<script lang="ts">
    import * as Avatar from "$lib/components/ui/avatar/index.js";
    import * as Tooltip from "$lib/components/ui/tooltip/index.js";
    import {members, guild_info} from "../../../stores"

    let members_value: UserData[] = []
    let guild_info_value: GuildInfo

	members.subscribe((value) => {
		members_value = value;
	})

    guild_info.subscribe((value) => {
		guild_info_value = value;
	})

</script>

<main class="w-[325px] h-[500px] border-2 border-border rounded flex flex-col bg-background">
    <div class="border-b border-border">
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Creation Date:</h1>
            <h1 class="text-right w-1/2">{guild_info_value?.created_at.toDateString() || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Members:</h1>
            <h1 class="text-right w-1/2">{guild_info_value?.member_count || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Roles:</h1>
            <h1 class="text-right w-1/2">{guild_info_value?.role_count || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Text Channels:</h1>
            <h1 class="text-right w-1/2">{guild_info_value?.text_channel_count || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Voice Channels:</h1>
            <h1 class="text-right w-1/2">{guild_info_value?.voice_channel_count || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Boosts:</h1>
            <h1 class="text-right w-1/2">{guild_info_value?.boosts || ""}</h1>
        </div>
    </div>
    <div class="overflow-auto grow">
        <ol class="h-full p-1">
            {#if members_value}
                {#each members_value.sort((a,b) => b.connection_time - a.connection_time) as member, i (member.id)}
                    <li class="w-full flex">
                        <div class="text-left w-3/4 text-nowrap flex-nowrap flex items-center justify-start overflow-ellipsis">
                            <h1>{i+1}</h1>
                            <Tooltip.Root closeOnPointerDown={false}>
                                <Tooltip.Trigger class="text-nowrap flex-nowrap flex items-center cursor-default w-full">
                                    <Avatar.Root class="mx-1 size-7">
                                        <Avatar.Image src={`https://cdn.discordapp.com/avatars/${member.id}/${member.avatar}.png`} alt="" />
                                        <Avatar.Fallback>{member.username[0].toUpperCase()}</Avatar.Fallback>
                                    </Avatar.Root>
                                    <h1 class="w-9/12 overflow-hidden overflow-ellipsis text-start">{member.nickname}</h1>
                                </Tooltip.Trigger>
                                <Tooltip.Content class="">
                                    <p class="w-full text-center mb-1 font-extrabold">{member.nickname}</p>
                                    {#if member.admin}
                                        <p>Admin</p>
                                    {/if}
                                    <p>Username: {member.username}</p>
                                    {#if member.global_name}
                                        <p>Global Nickname: {member.global_name}</p>
                                    {/if}
                                    {#if member.connection_time > 60}
                                        <p>Raw Connection Time: {(member.connection_time/60).toFixed(1)}hrs</p>
                                    {:else}
                                        <p>Raw Connection Time: {member.connection_time.toFixed(1)}mins</p>
                                    {/if}
                                    {#if member.muted_time > 60}
                                        <p>Muted Time: {(member.muted_time/60).toFixed(1)}hrs</p>
                                    {:else}
                                        <p>Muted Time: {member.muted_time.toFixed(1)}mins</p>
                                    {/if}
                                    {#if member.deafened_time > 60}
                                        <p>Deafened Time: {(member.deafened_time/60).toFixed(1)}hrs</p>
                                    {:else}
                                        <p>Deafened Time: {member.deafened_time.toFixed(1)}mins</p>
                                    {/if}
                                </Tooltip.Content>
                              </Tooltip.Root>
                        </div>
                        {#if member.connection_time > 60}
                            <div class="text-right w-1/4 flex justify-end items-center">
                                <h1>{((member.connection_time-member.muted_time-member.deafened_time)/60).toFixed(1)}hrs</h1>
                            </div>
                        {:else}
                            <div class="text-right w-1/4 flex justify-end items-center">
                                <h1>{(member.connection_time-member.muted_time-member.deafened_time).toFixed(1)}mins</h1>
                            </div>
                        {/if}
                    </li>
                {/each}
            
            {/if}
        </ol>
    </div>

</main>

<style>
    h1 {
        text-shadow: -1px -1px 0 #47003C, 1px -1px 0 #47003C, -1px 1px 0 #47003C, 1px 1px 0 #47003C;
    }
</style>
