<script lang="ts">
    import sedicon from "../assets/sedicon.webp"
    import * as Avatar from "$lib/components/ui/avatar/index.js";

    export let USER: User;

</script>

<main class="border-b-[1px] border-[#47003C] h-[10%]">
    <div class="flex items-center h-full w-full justify-between px-4">
        <div class="w-[25%]"><img src="{sedicon}" alt="" class="size-14 rounded-full"></div>
        <header class="seduction font-extrabold text-5xl">SEDUCTION</header>
        <div class="flex items-center justify-end w-[25%]">
            <span class="pr-4 font-bold">{USER.username}</span>
            <Avatar.Root>
                <Avatar.Image src={`https://cdn.discordapp.com/avatars/${USER.id}/${USER.avatar}.png`} alt="@shadcn" />
                <Avatar.Fallback>{USER.username[0].toUpperCase()}</Avatar.Fallback>
            </Avatar.Root>
        </div>
    </div>
</main>

<style>
    header.seduction {
        background: -webkit-linear-gradient(#2BFFD9, #FF7EE3);
        -webkit-background-clip: text;
        background-clip: 0;
        -webkit-text-fill-color: transparent;
    }
</style>
