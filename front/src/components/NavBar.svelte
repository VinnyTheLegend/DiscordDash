<script lang="ts">
    import { createEventDispatcher } from "svelte";
    const dispatch = createEventDispatcher();

    export let ROLES_DICT;

    export let USER: User;

    export let URLS: any;

    function userUpdate() {
        USER.get()
        console.log(USER)
        // dispatch("userUpdate");
    }

    export let echo: Function;

    function echoSubmit(e: SubmitEvent) {
        const target = e.target as HTMLFormElement;
        const formData = new FormData(target);
        const message = formData.get("message");
        target.reset();
        echo(message);
    }
</script>

<main>
    <div class="flex items-center">
        <div class="h-f">
            <button
                on:click={() => {
                    window.location.href = URLS.AUTH_URL;
                }}
            >
                Authenticate
            </button>
            <button on:click={userUpdate}> Discord Info </button>
        </div>
        {#if USER.member}
            <div class="flex p-2">
                <h1>Name: {USER.nickname}</h1>
                <h1>Admin: {USER.admin}</h1>
            </div>

            <button on:click={echo("test")}> test </button>

            <ul class="flex justify-around px-5">
                {#if USER.roles}
                    {#each USER.roles as role}
                        <span class="p-2 border-2 border-purple-500"
                            >{ROLES_DICT[role]}</span
                        >
                    {/each}
                {/if}
            </ul>

            <form
                action=""
                on:submit|preventDefault={echoSubmit}
                class="flex items-center"
            >
                <input type="text" name="message" class="h-5 text-black" />
                <button class="ml-2">Send</button>
            </form>
        {/if}
    </div>
</main>

<style>
</style>
