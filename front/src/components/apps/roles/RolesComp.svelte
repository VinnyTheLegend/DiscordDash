<script lang="ts">
  import { onMount } from "svelte";

  import { guild_info, members } from "../../../stores";
  import { fetch_guild, fetch_members, get_member } from "../../../utils";
  import * as Select from "$lib/components/ui/select/index.js";
  import Button from "$lib/components/ui/button/button.svelte";
  import { Trash } from "svelte-radix";

  let guild_info_value: GuildInfo;
  guild_info.subscribe((value) => {
    guild_info_value = value;
  });

  let members_value: UserData[];
  members.subscribe((value) => {
    members_value = value;
  });


    onMount(() => {
        if (typeof guild_info_value === "undefined") {
            fetch_guild();
        }
        if (members_value.length === 0) fetch_members()
        if (typeof guild_info_value === 'undefined') {
            fetch_guild()
        }

    });
</script>

<main class="size-full flex flex-col justify-start overflow-auto">
  <div class="p-5 m-auto">
    <h1 class="font-extrabold text-center mb-2">Optional Roles</h1>
    <div class="flex">
        <Select.Root>
            <Select.Trigger class="w-[180px]">
              <Select.Value placeholder="Add optional role" />
            </Select.Trigger>
            <Select.Content>
              <Select.Group>
                {#if (typeof guild_info_value !== 'undefined')}            
                    {#each guild_info_value?.roles as role}
                        {#if !role.optional && role.allowed_optional}
                            <Select.Item value={role.id} label={role.name}>{role.name}</Select.Item>
                        {/if}
                    {/each}
                {/if}
              </Select.Group>
            </Select.Content>
            <Select.Input name="addoptionalrole" />
          </Select.Root>
          <Button class="ml-2">Submit</Button>
    </div>      
  </div>
  <div class="flex-grow min-h-0 min-w-0 mb-5 flex flex-col px-5">
    <ul class="border-2 border-border bg-background rounded-lg max-h-full flex flex-col overflow-auto items-center mx-auto min-w-[30%]">
        {#if (typeof guild_info_value !== 'undefined')}            
            {#each guild_info_value?.roles as role}
                {#if role.optional}
                <li class="flex w-full p-2 items-center justify-between">
                    <div class="flex items-center">
                        <Button variant="destructive" class="size-8 p-0">
                            <Trash/>
                        </Button>
                        <h1 class="ml-2">{role.name}</h1>
                    </div>
                    <div class="flex items-center ml-5">
                        {#if members_value.length !== 0}
                            <span>
                                Added By: {get_member(role.added_by, members_value)}
                            </span>
                        {/if}
                    </div>
                </li>
                {/if}
            {/each}
        {/if}
    </ul>
  </div>
</main>

<style>
  h1 {
    text-shadow:
      -1px -1px 0 #47003c,
      1px -1px 0 #47003c,
      -1px 1px 0 #47003c,
      1px 1px 0 #47003c;
  }
</style>
