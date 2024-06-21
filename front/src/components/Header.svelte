<script lang="ts">
    import sedicon from "../assets/sedicon.webp"
    import * as Avatar from "$lib/components/ui/avatar/index.js";
    import * as DropdownMenu from "$lib/components/ui/dropdown-menu";

    import {URLS} from "../utils"

    export let USER: User;

</script>

<main class="border-b-[1px] border-[#47003C] h-[10%] bg-black">
    <div class="flex items-center h-full w-full justify-between px-4">
        <div class="w-[25%]"><img src="{sedicon}" alt="" class="size-14 rounded-full"></div>
        <button class="seduction font-extrabold text-5xl" on:click={() => {window.location.href = URLS.FRONT_URL}}>SEDUCTION</button>
        <div class="flex items-center justify-end w-[25%]">
            <span class="pr-4 font-bold">{USER.username}</span>
            <DropdownMenu.Root>
                <DropdownMenu.Trigger>
                    <Avatar.Root>
                        <Avatar.Image src={`https://cdn.discordapp.com/avatars/${USER.id}/${USER.avatar}.png`} alt="@shadcn" />
                        <Avatar.Fallback>{USER.username[0].toUpperCase()}</Avatar.Fallback>
                    </Avatar.Root>
                </DropdownMenu.Trigger>
                <DropdownMenu.Content class="">
                  <DropdownMenu.Group>
                    <DropdownMenu.Label>My Account</DropdownMenu.Label>
                    <DropdownMenu.Separator />
                    <DropdownMenu.Item>Role Selection</DropdownMenu.Item>
                    <DropdownMenu.Item class="bg-destructive data-[highlighted]:bg-red-700">Sign Out</DropdownMenu.Item>
                  </DropdownMenu.Group>
                </DropdownMenu.Content>
              </DropdownMenu.Root>
        </div>
    </div>
</main>

<style>
    button.seduction {
        background: -webkit-linear-gradient(#2BFFD9, #FF7EE3);
        -webkit-background-clip: text;
        background-clip: 0;
        -webkit-text-fill-color: transparent;
    }
</style>
