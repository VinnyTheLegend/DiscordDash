<script lang="ts">
    import { echo, URLS, ROLES_DICT } from "../utils";
    import sedicon from "../assets/sedicon.webp"

    export let USER: User;

    function echoSubmit(e: SubmitEvent) {
        const target = e.target as HTMLFormElement;
        const formData = new FormData(target);
        const message = formData.get("message");
        target.reset();
        if (typeof message === "string" && message != "") {
            echo(message);
        }
    }
    
    function getAvatarUrl(id: bigint, avatar: string): string {
        let url = `https://cdn.discordapp.com/avatars/${id}/${avatar}.png`
        return url
    }
</script>

<main class="border-b-[1px] border-[#47003C] h-[10%]">
    <div class="flex items-center h-full w-full justify-between px-4">
        <div class="w-[11%]"><img src="{sedicon}" alt="" class="size-14 rounded-full"></div>
        <header class="seduction font-extrabold text-5xl">SEDUCTION</header>
        <div class="flex items-center justify-center w-[11%]">
            <span class="pr-4 font-bold">{USER.username}</span>
            <img src="{getAvatarUrl(USER.id, USER.avatar)}" alt="" class="size-14 rounded-full">
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
