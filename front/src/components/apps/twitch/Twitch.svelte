<script lang="ts">
    import Button from "$lib/components/ui/button/button.svelte";
    import Input from "$lib/components/ui/input/input.svelte";
    import Separator from "$lib/components/ui/separator/separator.svelte";
    import Trash from "svelte-radix/Trash.svelte"
    import { onMount } from 'svelte';

    import { members } from "../../../stores"
    import { fetch_members, URLS } from "../../../utils";

    interface TwitchStream {
        user_login: string
        added_by: string
    }

    let members_value: UserData[] = []
    members.subscribe((value) => {
        members_value = value;
    })

    onMount(() => {
        if (members_value.length === 0) fetch_members()
    })
    
    let twitch_streams: TwitchStream[]
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
            return
        } 
            
        for (let i = 0; i < twitch_streams.length; i++) {
            if (twitch_streams[i].user_login === stream_to_add) {
                console.log("stream already followed")
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

    }
</script>

<main class="size-full flex flex-col justify-start items-center p-5">
    <form on:submit|preventDefault={add_stream} class="flex bg-background p-2 rounded-lg border-2 border-border">   
        <Button type="submit">Add Stream</Button> <Input placeholder="stream name" bind:value={stream_to_add}/>
    </form>
    <ul class="border-2 border-border bg-background w-[500px] mt-5 flex flex-col items-center">
        {#if twitch_streams}
            {#each twitch_streams as stream}
                <li class="flex w-full p-2 items-center justify-between">    
                    <div class="flex items-center">
                        <Button variant="destructive" class="size-8 p-0">
                            <Trash/>
                        </Button>
                        <h1 class="ml-2">{stream.user_login}</h1>
                    </div>
                    <div class="flex items-center">
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
