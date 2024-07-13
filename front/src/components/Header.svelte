<script lang="ts">
    import sedicon from "../assets/sedicon.webp"
    import * as Avatar from "$lib/components/ui/avatar/index.js";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";
    import * as Dialog from "$lib/components/ui/dialog";
    import { Checkbox } from "$lib/components/ui/checkbox/index.js";
    import { Label } from "$lib/components/ui/label/index.js";
    import { Button } from "$lib/components/ui/button";
    import { createEventDispatcher } from 'svelte';

    import {URLS} from "../utils"

    export let USER: User;

    let optional_roles = [{id: "1222684351054221312", name: 'Twitch Notifications', checked: false}, {id: "850013094758842400", name: 'Drops', checked: false}]
    if (USER.roles != null) {
        optional_roles.forEach(role => {
            if (USER.roles?.includes(role.id)){
                role.checked = true
            }
            console.log(`${role.name}: ${role.checked}`)
        })
    }

    const url = new URL(`${URLS.USER_URL}/roles`)
    function roleChange(role: {id: string, name: string, checked: boolean}) {
        let operation
        role.checked ? operation = 'remove' : operation = 'add'
        url.searchParams.delete('operation')
        url.searchParams.delete('role_id')
        url.searchParams.append('operation', operation)
        url.searchParams.append('role_id', role.id)
        console.log(url)
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
            USER.get()
            optional_roles.forEach((role, i) => {
                if (USER.roles?.includes(role.id)){
                    optional_roles[i].checked = true
                } else {
                    optional_roles[i].checked = false
                    
                }
                console.log(USER.roles)
            })
        })
        .catch((error) => {
            optional_roles.forEach(role => {
                if (USER.roles?.includes(role.id)){
                    role.checked = true
                } else {
                    role.checked = false
                }
                console.log(`${role.name}: ${role.checked}`)
            })
            optional_roles = optional_roles
            console.log(error);
            return [];
        });
    }


    
    const dispatch = createEventDispatcher<{toggleSidebar: boolean}>();

    let shown = false
    function toggleSidebar() {
        shown = !shown
        dispatch('toggleSidebar', shown);
    }

</script>

<main class="border-b-[1px] border-[#47003C] h-20 w-full bg-black flex items-center relative flex-shrink-0">
        <button on:click={toggleSidebar} class="absolute left-5"><img src="{sedicon}" alt="" class="size-14 rounded-full"></button>
        <button class="seduction m-auto font-extrabold text-5xl" on:click={() => {window.location.href = URLS.FRONT_URL}}>SEDUCTION</button>
        <div class="right-5 absolute flex items-center justify-end">
            <span class="pr-4 font-bold">{USER.username}</span>
            <Dialog.Root>
                <DropdownMenu.Root>
                    <DropdownMenu.Trigger>
                        <Avatar.Root>
                            <Avatar.Image src={`https://cdn.discordapp.com/avatars/${USER.id}/${USER.avatar}.png`} alt="" />
                            <Avatar.Fallback>{USER.username[0].toUpperCase()}</Avatar.Fallback>
                        </Avatar.Root>
                    </DropdownMenu.Trigger>
                    <DropdownMenu.Content class="border-border">
                        <DropdownMenu.Group>
                            <DropdownMenu.Label>My Account</DropdownMenu.Label>
                            <DropdownMenu.Separator />
                            <Dialog.Trigger class="w-full"><DropdownMenu.Item>Role Selection</DropdownMenu.Item></Dialog.Trigger>
                            <DropdownMenu.Item class="bg-destructive data-[highlighted]:bg-red-700" on:click={() => window.location.href=`${URLS.BASE_URL}/logout`}>Sign Out</DropdownMenu.Item>
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
                                <Checkbox id="terms" bind:checked={role.checked} onCheckedChange={() => roleChange(role)} aria-labelledby="terms-label" />
                                <Label
                                id="terms-label"
                                for="terms"
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
        background: -webkit-linear-gradient(#2BFFD9, #FF7EE3);
        -webkit-background-clip: text;
        background-clip: 0;
        -webkit-text-fill-color: transparent;
    }

    @media(max-width:600px) {
    .seduction {
        visibility: hidden;
    }
}
</style>
