<script lang="ts">
    import Button from "$lib/components/ui/button/button.svelte";
    import Input from "$lib/components/ui/input/input.svelte";
    import Separator from "$lib/components/ui/separator/separator.svelte";
    import Trash from "svelte-radix/Trash.svelte"
    import { onMount } from 'svelte';

    import { members } from "../../../stores"
    import { fetch_members, URLS } from "../../../utils";

    let members_value: UserData[] = []
    members.subscribe((value) => {
        members_value = value;
    })
    
    
    let twitch_streams: TwitchStream[] = []
    onMount(() => {
        fetch(URLS.BASE_URL+'/api/twitchstreams', { mode: "cors", credentials: "include" })
        .then((response) => {
        if (response.status === 400) {
            return response.json().then((data) => {
            throw new Error(data.detail || "Bad request");
            });
        }
        return response.json();
        })
        .then((data: TwitchStream[]) => {
            twitch_streams = data
            console.log(twitch_streams)
        })
        .catch((error) => {
            console.log(error);
        
        });
        if (members_value.length === 0) fetch_members()
    })
    



    function get_member(id: string): string {
        const member = members_value.find(member => member.id === id);
        if (member) {
            console.log(member.nickname);
            return member.nickname || member.global_name;
        }
        return 'Unknown'
    }

    let stream_to_add: string
    let stream_add_url = new URL(URLS.BASE_URL+'/api/twitchstreams/add')
    function add_stream(): void {
        console.log(stream_to_add)
        if (stream_to_add.includes(" ") || stream_to_add === "") {
            console.log("invalid stream name")
            stream_to_add = ""

            return
        } 
            
        for (let i = 0; i < twitch_streams.length; i++) {
            if (twitch_streams[i].user_login === stream_to_add) {
                console.log("stream already followed")
                stream_to_add = ""

                return
            }
        }
        stream_add_url.searchParams.set('stream', stream_to_add)
        fetch(stream_add_url, { mode: "cors", credentials: "include", method: "POST" })
        .then((response) => {
            if (response.status !== 200) {
                return response.json().then((data) => {
                throw new Error(data.detail || "Bad request");
                });
            }
            return response.json();
        })
        .then((data: TwitchStream) => {
            twitch_streams.push(data)
            twitch_streams = twitch_streams
            console.log("added: ", data)
        })
        .catch((error) => {
            console.log(error);
        
        });
        stream_to_add = ""
    }

    let stream_remove_url = new URL(URLS.BASE_URL+'/api/twitchstreams/remove')
    function remove_stream(stream: string): void {
        if (stream.includes(" ") || stream === "") {
            console.log("invalid stream name")
            return
        } 
        
        let found = false
        let stream_index: number
        for (let i = 0; i < twitch_streams.length; i++) {
            if (twitch_streams[i].user_login === stream) {
                stream_index = i 
                found = true
                break
            }
        }
        if (found === false) {
            console.log("stream not followed")
            return
        }
        stream_remove_url.searchParams.set('stream', stream)
        console.log(stream_remove_url)

        fetch(stream_remove_url, { mode: "cors", credentials: "include", method: 'DELETE' })
        .then((response) => {
        if (response.status !== 200) {
            return response.json().then((data) => {
            throw new Error(data.detail || "Bad request");
            });
        }
        return response.json();
        })
        .then((data: TwitchStream) => {
            console.log(twitch_streams[stream_index])
            twitch_streams =  twitch_streams.filter(s => s.user_login !== stream);
            console.log("removed: ", data)
        })
        .catch((error) => {
            console.log(error);
        
        });
    }

</script>

<main class="size-full flex flex-col justify-start overflow-auto">
    <div class="p-5 m-auto">
        <form on:submit|preventDefault={add_stream} class="flex">
            <Button type="submit">Add Stream</Button> <Input placeholder="stream name" bind:value={stream_to_add} class="ml-2 bg-gray-900"/>
        </form>
    </div>
    <div class="flex-grow min-h-0 min-w-0 mb-5 flex flex-col px-5">
        <ul class="border-2 border-border bg-background rounded-lg max-h-full flex flex-col overflow-auto items-center mx-auto min-w-[50%]">
            {#if twitch_streams}
                {#each twitch_streams as stream}
                    <li class="flex w-full p-2 items-center justify-between">
                        <div class="flex items-center">
                            <Button on:click={() => remove_stream(stream.user_login)} variant="destructive" class="size-8 p-0">
                                <Trash/>
                            </Button>
                            <h1 class="ml-2">{stream.user_login}</h1>
                        </div>
                        <div class="flex items-center ml-5">
                            {#if members_value.length !== 0}
                                <span>
                                    Added By: {get_member(stream.added_by)}
                                </span>
                            {/if}
                        </div>
                    </li>
                    <Separator class="w-[90%]"/>
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
