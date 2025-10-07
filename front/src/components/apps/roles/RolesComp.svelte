<script lang="ts">
  import { guild_info, members } from "../../../stores";
  import { fetch_guild, get_member, URLS } from "../../../utils";
  import * as Select from "$lib/components/ui/select/index.js";
  import Button from "$lib/components/ui/button/button.svelte";
  import { Trash } from "svelte-radix";
  import type { Selected } from "bits-ui"
  import { toast } from "svelte-sonner";

  let guild_info_value: GuildInfo = $guild_info
  guild_info.subscribe((value) => {
    guild_info_value = value;
  });

  let members_value: UserData[] = $members
  members.subscribe((value) => {
    members_value = value;
  });

  export let visible = false;
  $: if (visible) {
    fetch_guild()
  }

  
  let role_to_add: Selected<string | undefined>
  function add_role(): void {
    console.log(role_to_add)
    if (!role_to_add.value) {return}
    let optional_role_add_url = new URL(URLS.BASE_URL+'/api/guild/roles/optional/add')
    optional_role_add_url.searchParams.set('role_add_id', role_to_add.value)
    fetch(optional_role_add_url, { mode: "cors", credentials: "include", method: "POST" })
      .then((response) => {
          if (response.status !== 200) {
              return response.json().then((data) => {
              throw new Error(data.detail || "Bad request");
              });
          }
          return response.json();
      })
      .then((data: TwitchStream) => {
          fetch_guild()
          toast.success('Role added.')
      })
      .catch((error) => {
          console.log(error);
          fetch_guild()
          toast.error('Operation failed.')
      });
    role_to_add = {value:undefined, label:undefined}
  }

  function remove_role(role_id: string): void {
    let optional_role_remove_url = new URL(URLS.BASE_URL+'/api/guild/roles/optional/remove')
    optional_role_remove_url.searchParams.set('role_remove_id', role_id)
    fetch(optional_role_remove_url, { mode: "cors", credentials: "include", method: "POST" })
      .then((response) => {
          if (response.status !== 200) {
              return response.json().then((data) => {
              throw new Error(data.detail || "Bad request");
              });
          }
          return response.json();
      })
      .then((data: TwitchStream) => {
          fetch_guild()
          toast.success('Role removed.')
      })
      .catch((error) => {
          console.log(error);
          fetch_guild()
          toast.error('Operation failed.')
      });
  }

</script>

<main class="size-full flex flex-col justify-start overflow-auto">
  <div class="p-5 m-auto">
    <h1 class="font-extrabold text-center mb-2">Optional Roles</h1>
    <div class="flex">
        <Select.Root bind:selected={role_to_add}>
            <Select.Trigger  class="w-52 bg-gray-900">
              <Select.Value placeholder="Add optional role" />
            </Select.Trigger>
            <Select.Content class="border-border">
              <Select.Group>
                {#if (typeof guild_info_value !== 'undefined')}            
                    {#each guild_info_value?.roles as role}
                        {#if !role.optional && role.allowed_optional}
                            <Select.Item value={role.id} label={role.name}> {role.name} </Select.Item>
                        {/if}
                    {/each}
                {/if}
              </Select.Group>
            </Select.Content>
            <Select.Input name="addoptionalrole" />
          </Select.Root>
          <Button on:click={add_role} class="ml-2">Submit</Button>
    </div>      
  </div>
  <div class="flex-grow min-h-0 min-w-0 mb-5 flex flex-col px-5">
    <ul class="border-2 border-border bg-background rounded-lg max-h-full flex flex-col overflow-auto items-center mx-auto min-w-[50%]">
        {#if (typeof guild_info_value !== 'undefined')}            
            {#each guild_info_value?.roles as role}
                {#if role.optional}
                <li class="flex w-full p-2 items-center justify-between">
                    <div class="flex items-center">
                        <Button on:click={() => {remove_role(role.id)}} variant="destructive" class="size-8 p-0">
                            <Trash/>
                        </Button>
                        <h1 class="ml-2">{role.name}</h1>
                    </div>
                    <div class="flex items-center ml-5">
                        {#if members_value.length !== 0}
                            <span class="text-right">
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
