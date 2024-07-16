<script lang="ts">
  import sedicon from "../assets/sedicon.webp";
  import * as Avatar from "$lib/components/ui/avatar/index.js";
  import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
  import * as Dialog from "$lib/components/ui/dialog";
  import { toast } from "svelte-sonner"
  import { Checkbox } from "$lib/components/ui/checkbox/index.js";
  import { Label } from "$lib/components/ui/label/index.js";
  import { createEventDispatcher } from "svelte";
  import { guild_info } from "../stores";
  import { onMount } from "svelte";

  import { URLS, fetch_guild } from "../utils";

  export let USER: User;

  let guild_info_value: GuildInfo;
  let optional_roles: { id: string; name: string; checked: boolean }[];

  function processRoles(
    roles: Role[]
  ): { id: string; name: string; checked: boolean }[] {
    let processed_roles: { id: string; name: string; checked: boolean }[] = [];
    roles.forEach((role) => {
      let is_checked: boolean = false;
      if (role.optional) {
        if (USER.roles && role.id in USER.roles) is_checked = true;
        processed_roles.push({
          id: role.id,
          name: role.name,
          checked: is_checked,
        });
      }
    });
    return processed_roles;
  }

  guild_info.subscribe((value) => {
    guild_info_value = value;
    if (value) {
      optional_roles = processRoles(value.roles);
      for (let i in optional_roles) {
        if (USER.roles?.includes(optional_roles[i].id)) {
          optional_roles[i].checked = true;
        }
        console.log(`${optional_roles[i].name}: ${optional_roles[i].checked}`);
      }
      optional_roles = optional_roles;
    }
  });

  onMount(() => {
    if (typeof guild_info_value === "undefined") {
      fetch_guild();
    } else {
      optional_roles = processRoles(guild_info_value.roles);
      for (let i in optional_roles) {
        if (USER.roles?.includes(optional_roles[i].id)) {
          optional_roles[i].checked = true;
        }
        console.log(`${optional_roles[i].name}: ${optional_roles[i].checked}`);
      }
      optional_roles = optional_roles;
    }
  });

  const url = new URL(`${URLS.USER_URL}/roles`);
  function roleChange(role: { id: string; name: string; checked: boolean }) {
    let operation;
    role.checked ? (operation = "remove") : (operation = "add");
    url.searchParams.delete("operation");
    url.searchParams.delete("role_id");
    url.searchParams.append("operation", operation);
    url.searchParams.append("role_id", role.id);
    console.log(url);
    fetch(url, { mode: "cors", credentials: "include" })
      .then((response) => {
        if (response.status === 400) {
          return response.json().then((data) => {
            throw new Error(data.detail || "Bad request");
          });
        }
        return response.json();
      })
      .then((data) => {
        Object.assign(USER, data);
        USER.get();
        optional_roles.forEach((role, i) => {
          if (USER.roles?.includes(role.id)) {
            optional_roles[i].checked = true;
          } else {
            optional_roles[i].checked = false;
          }
          console.log(USER.roles);
        });
        role.checked ? toast.success('Role added') : toast.success('Role removed.')
      })
      .catch((error) => {
        optional_roles.forEach((role) => {
          if (USER.roles?.includes(role.id)) {
            role.checked = true;
          } else {
            role.checked = false;
          }
          console.log(`${role.name}: ${role.checked}`);
        });
        optional_roles = optional_roles;
        console.log(error);
        toast.error('Operation failed')
        return [];
      });
  }

  const dispatch = createEventDispatcher<{ toggleSidebar: boolean }>();

  let shown = false;
  function toggleSidebar() {
    shown = !shown;
    dispatch("toggleSidebar", shown);
  }
</script>

<main
  class="border-b-[1px] border-[#47003C] h-20 w-full bg-black flex items-center relative flex-shrink-0"
>
  <button on:click={toggleSidebar} class="absolute left-5">
    <img src={sedicon} alt="" class="size-14 rounded-full" />
  </button>
  <button
    class="seduction m-auto font-extrabold text-5xl"
    on:click={() => {
      window.location.href = URLS.FRONT_URL;
    }}>SEDUCTION</button
  >
  <div class="right-5 absolute flex items-center justify-end">
    <span class="pr-4 font-bold">{USER.username}</span>
    <Dialog.Root>
      <DropdownMenu.Root>
        <DropdownMenu.Trigger>
          <Avatar.Root>
            <Avatar.Image
              src={`https://cdn.discordapp.com/avatars/${USER.id}/${USER.avatar}.png`}
              alt=""
            />
            <Avatar.Fallback>{USER.username[0].toUpperCase()}</Avatar.Fallback>
          </Avatar.Root>
        </DropdownMenu.Trigger>
        <DropdownMenu.Content class="border-border">
          <DropdownMenu.Group>
            <DropdownMenu.Label>My Account</DropdownMenu.Label>
            <DropdownMenu.Separator />
            {#if USER.member}
              <Dialog.Trigger class="w-full">
                <DropdownMenu.Item>Role Selection</DropdownMenu.Item>
              </Dialog.Trigger>
            {/if}
            <DropdownMenu.Item
              class="bg-destructive data-[highlighted]:bg-red-700"
              on:click={() =>
                (window.location.href = `${URLS.BASE_URL}/logout`)}
              >Sign Out
            </DropdownMenu.Item>
          </DropdownMenu.Group>
        </DropdownMenu.Content>
      </DropdownMenu.Root>
      <Dialog.Content class="border-border">
        <Dialog.Header>
          <Dialog.Title class="text-center">Role Selection</Dialog.Title>
        </Dialog.Header>
        <div class="grid grid-cols-3">
          {#each optional_roles as role}
            <div class="flex items-center space-x-2 w-auto mx-4 my-2">
              <Checkbox
                id="{role.id}"
                bind:checked={role.checked}
                onCheckedChange={() => roleChange(role)}
                aria-labelledby="terms-label"
              />
              <Label
                for="{role.id}"
                class="text-sm font-medium leading-none peer-disabled:cursor-not-allowed peer-disabled:opacity-70 text-center"
              >
                {role.name}
              </Label>
            </div>
          {/each}
        </div>
      </Dialog.Content>
    </Dialog.Root>
  </div>
</main>

<style>
  button.seduction {
    background: -webkit-linear-gradient(#2bffd9, #ff7ee3);
    -webkit-background-clip: text;
    background-clip: 0;
    -webkit-text-fill-color: transparent;
  }

  @media (max-width: 600px) {
    .seduction {
      visibility: hidden;
    }
  }
</style>
