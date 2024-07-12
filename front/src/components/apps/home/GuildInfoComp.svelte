<script lang="ts">
    import { fetch_members, URLS } from "../../../utils";
    import * as Avatar from "$lib/components/ui/avatar/index.js";
    import * as Tooltip from "$lib/components/ui/tooltip/index.js";
    import {members} from "../../../stores"
  import { onMount } from "svelte";

    let members_value: UserData[] = []
    let guild_info: GuildInfo

	members.subscribe((value) => {
		members_value = value;
	})

    onMount(() => {
        if (members_value.length === 0) fetch_members()
    })

    fetch(URLS.BASE_URL+'/api/guild', { mode: "cors", credentials: "include" })
        .then((response) => {
          if (response.status === 400) {
            return response.json().then((data) => {
              throw new Error(data.detail || "Bad request");
            });
          }
          return response.json();
        })
        .then((data: GuildInfo) => {
            data.created_at = new Date(data.created_at)
            guild_info = data
            console.log(guild_info)
        })
        .catch((error) => {
            console.log(error);
            return [];
        });
</script>

<main class="w-[325px] h-[500px] border-2 border-border rounded flex flex-col bg-background">
    <div class="border-b border-border">
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Creation Date:</h1>
            <h1 class="text-right w-1/2">{guild_info?.created_at.toDateString() || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Members:</h1>
            <h1 class="text-right w-1/2">{guild_info?.member_count || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Roles:</h1>
            <h1 class="text-right w-1/2">{guild_info?.role_count || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Text Channels:</h1>
            <h1 class="text-right w-1/2">{guild_info?.text_channel_count || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Voice Channels:</h1>
            <h1 class="text-right w-1/2">{guild_info?.voice_channel_count || ""}</h1>
        </div>
        <div class="w-full flex px-2">
            <h1 class="text-left w-1/2">Boosts:</h1>
            <h1 class="text-right w-1/2">{guild_info?.boosts || ""}</h1>
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
                                </Tooltip.Content>
                              </Tooltip.Root>
                        </div>
                        <div class="text-right w-1/4 flex justify-end items-center">
                            <h1>{member.connection_time.toFixed(1)}mins</h1>
                        </div>
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
