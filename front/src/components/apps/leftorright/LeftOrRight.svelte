<script lang="ts">
    import Button from "$lib/components/ui/button/button.svelte";
    import Input from "$lib/components/ui/input/input.svelte";
    import Separator from "$lib/components/ui/separator/separator.svelte";
    import Trash from "svelte-radix/Trash.svelte"
    import * as Tooltip from "$lib/components/ui/tooltip/index.js";
    import * as Dialog from "$lib/components/ui/dialog/index.js";

    import { onMount } from 'svelte';

    import { members } from "../../../stores"
    import { update_member_store, URLS } from "../../../utils";
    import { toast } from "svelte-sonner";

    let members_value: UserData[] = []
    members.subscribe((value) => {
        members_value = value;
    })
    
    export async function fetch_leftorrights(skip: number = 0, limit: number = 100): Promise<LeftOrRight[] | void> {
        let lor_url = new URL(URLS.BASE_URL+'/api/leftorright')
        lor_url.searchParams.set('skip', skip.toString())
        lor_url.searchParams.set('limit', limit.toString())


        return fetch(lor_url, { mode: "cors", credentials: "include" })
        .then((response) => {
        if (response.status === 400) {
            return response.json().then((data) => {
            throw new Error(data.detail || "Bad request");
            });
        }
        return response.json();
        })
        .then((data: LeftOrRight[]) => {
            return data
        })
        .catch((error) => {
            console.log(error);
            return;
        });
    }

    let lors: LeftOrRight[] = []
    export async function update_leftorrights() {
        let new_lor_value: LeftOrRight[] = []
        let fetched_lor = await fetch_leftorrights()
        if (!fetched_lor) return
        new_lor_value.push(...fetched_lor)
        let toskip = 100
        while (fetched_lor && fetched_lor.length >= 100) {
            fetched_lor = await fetch_leftorrights(toskip)
            toskip = toskip + 100
            if (fetched_lor) new_lor_value.push(...fetched_lor)
        }
        lors = new_lor_value
        console.log(lors)
    }
    
    onMount(() => {
       update_leftorrights()
       if (members_value.length === 0) update_member_store()
    })
    

    function get_member(id: string): string {
        const member = members_value.find(member => member.id === id);
        if (member) {
            console.log(member.nickname);
            return member.nickname || member.global_name;
        }
        return 'Unknown'
    }

    let lor_to_add_name: string
    let lor_to_add_img_url: string
    let lor_add_url = new URL(URLS.BASE_URL+'/api/leftorright/add')
    function add_lor(): void {
        console.log(lor_to_add_name)
        if (lor_to_add_img_url === "" || lor_to_add_name === "") {
            toast.error('Invalid image details')

            return
        } 
            
        lor_add_url.searchParams.set('name', lor_to_add_name)
        lor_add_url.searchParams.set('img_url', lor_to_add_img_url)
        fetch(lor_add_url, { mode: "cors", credentials: "include", method: "POST" })
        .then((response) => {
            if (response.status !== 200) {
                return response.json().then((data) => {
                throw new Error(data.detail || "Bad request");
                });
            }
            return response.json();
        })
        .then((data: LeftOrRight) => {
            lors.push(data)
            lors = lors
            toast.success('Image added.')
        })
        .catch((error) => {
            console.log(error);
            toast.error("Operation failed.")
        });
        lor_to_add_name = ""
        lor_to_add_img_url = ""
    }

    let lor_remove_url = new URL(URLS.BASE_URL+'/api/leftorright/remove')
    function remove_lor(lor: string): void {
        if (lor === "") {
            toast.error("Invalid image.")
            return
        } 
        
        let found = false
        let lor_index: number
        for (let i = 0; i < lors.length; i++) {
            if (lors[i].name === lor) {
                lor_index = i 
                found = true
                break
            }
        }
        if (found === false) {
            toast.error("Image not found.")
            return
        }
        lor_remove_url.searchParams.set('name', lor)

        fetch(lor_remove_url, { mode: "cors", credentials: "include", method: 'DELETE' })
        .then((response) => {
        if (response.status !== 200) {
            return response.json().then((data) => {
            throw new Error(data.detail || "Bad request");
            });
        }
        return response.json();
        })
        .then((data: number) => {
            lors =  lors.filter(s => s.name !== lor);
            toast.success(`Removed ${data} image(s).`)
        })
        .catch((error) => {
            console.log(error);
            toast.error("Operation failed.")
        });
    }

</script>

<main class="size-full flex flex-col justify-start overflow-auto">
    <div class="p-5 m-auto">
        <form on:submit|preventDefault={add_lor} class="flex">
            <Button type="submit">Add Image</Button> 
            <Input placeholder="image name" bind:value={lor_to_add_name} class="ml-2 bg-gray-900"/>
            <Input placeholder="image url" bind:value={lor_to_add_img_url} class="ml-2 bg-gray-900"/>
        </form>
    </div>
    <div class="flex-grow min-h-0 min-w-0 mb-5 flex flex-col px-5">
        <ul class="border-2 border-border bg-background rounded-lg max-h-full flex flex-col overflow-auto items-center mx-auto min-w-[50%]">
            {#if lors}
                {#each lors as lor}
                    <li class="flex w-full p-2 items-center justify-between">
                        <div class="flex items-center">
                            <Button on:click={() => remove_lor(lor.name)} variant="destructive" class="size-8 p-0">
                                <Trash/>
                            </Button>
                            <Dialog.Root>
                                <Dialog.Trigger>                            
                                    <Tooltip.Root disableHoverableContent>
                                        <Tooltip.Trigger>
                                            <h1 class="ml-2">{lor.name}</h1>
                                        </Tooltip.Trigger>
                                        <Tooltip.Content class="h-[300px] w-[200px] flex justify-center items-center overflow-hidden">
                                            <img src="{lor.img_url}" alt="">
                                        </Tooltip.Content>
                                    </Tooltip.Root>
                                </Dialog.Trigger>
                                <Dialog.Content class="p-7 flex justify-center items-center bg-black border-border">
                                    <div class="size-full flex justify-center items-center object-contain">
                                        <a href="{lor.img_url}" target="_blank">
                                            <img src="{lor.img_url}" alt="">
                                        </a>
                                    </div>
                                </Dialog.Content>
                              </Dialog.Root>
                        </div>
                        <div class="flex items-center ml-5">
                            {#if members_value.length !== 0}
                                <span class="text-right">
                                    Added By: {get_member(lor.added_by)}
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
