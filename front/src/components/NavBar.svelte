<script lang="ts">
    import { createEventDispatcher } from 'svelte'
    const dispatch = createEventDispatcher()
  
    export let ROLES_DICT
  
    function AuthRedirect() {
      window.location.href = URLS.AUTH_URL;
    }
  
    export let USER_INFO: UserData | null

    export let URLS: any
  
    function userUpdate() {
        dispatch('userUpdate')
    }
    
    function Echo(e: SubmitEvent) {
      const target = e.target as HTMLFormElement
      const formData = new FormData(target)
      const message = formData.get("message")
      target.reset()
  
      fetch(URLS.BASE_URL + "/api/echo", {
        mode: 'cors', 
        credentials: 'include',
        method: "POST",
        headers: {'Content-Type': 'application/json'}, 
        body: JSON.stringify({message: message})
      }).then(res => {
        console.log("Echo response", res);
      });
    }
  
  </script>
  
  <main>
    <div class="flex items-center">
      <button on:click={AuthRedirect}> Authenticate </button>
      <button on:click={userUpdate}> Discord Info </button>
      {#if USER_INFO}
      
        <div class="flex p-2">
          <h1>Name: {USER_INFO.nickname}</h1>
          <h1>Admin: {USER_INFO.admin}</h1>
        </div>
  
        <button
        on:click={async () => {
          fetch(URLS.BASE_URL + "/api/test", {mode: 'cors', credentials: 'include'})
            .then((response) => response.json())
            .then((data) => {
              console.log(data);
            })
            .catch((error) => {
              console.log(error);
              return [];
            });
        }}
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
  
        <form action="" on:submit|preventDefault={Echo} class="flex items-center">
          <input type="text" name="message" class="h-5 text-black">
          <button class="ml-2">Send</button>
        </form>
  
      {/if}
    </div>
  
  </main>
  
  <style>
  
  </style>
  