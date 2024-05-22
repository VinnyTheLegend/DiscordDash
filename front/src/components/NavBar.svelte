<script lang="ts">
    import { createEventDispatcher } from 'svelte'
    const dispatch = createEventDispatcher()
  
    export let ROLES_DICT
  
    export let USER_INFO: UserData | null

    export let URLS: any
  
    function userUpdate() {
        dispatch('userUpdate')
    }
    
    export let echo: Function

    function echoSubmit(e: SubmitEvent) {
        const target = e.target as HTMLFormElement
        const formData = new FormData(target)
        const message = formData.get("message")
        target.reset()
        echo(message)
    }

  </script>
  
  <main>
    <div class="flex items-center">
      <button on:click={() => {window.location.href = URLS.AUTH_URL}}> Authenticate </button>
      <button on:click={userUpdate}> Discord Info </button>
      {#if USER_INFO}
      
        <div class="flex p-2">
          <h1>Name: {USER_INFO.nickname}</h1>
          <h1>Admin: {USER_INFO.admin}</h1>
        </div>
  
        <button
        on:click={echo('test')}
      >
        test
      </button>
  
        <ul>
          {#if USER_INFO.roles}
            {#each USER_INFO.roles as role}
             <span class="p-2 m-2 border-2 border-purple-500">{ROLES_DICT[role]}</span>
            {/each}
          {/if}
        </ul>
  
        <form action="" on:submit|preventDefault={echoSubmit} class="flex items-center">
          <input type="text" name="message" class="h-5 text-black">
          <button class="ml-2">Send</button>
        </form>
  
      {/if}
    </div>
  
  </main>
  
  <style>
  
  </style>
  