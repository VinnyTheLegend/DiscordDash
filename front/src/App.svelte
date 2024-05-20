<script lang="ts">
  const BASE_URL: string = "https://localhost:8000"
  const AUTH_URL: string = BASE_URL + "/discord/authenticate";
  const ME_URL: string = BASE_URL + "/discord/me";
  const URL_PARAMS = new URLSearchParams(window.location.search);

  const ROLES_DICT: { [id: string] : string; } = {
    "591686220996935691": "Warlord",
    "591686523142012948": "General",
    "591687458819932172": "Veteran",
    "591687038902992928": "Member"
  }

  let token: string | null = URL_PARAMS.get("token");
  let state: string | null = URL_PARAMS.get("state");

  function AuthRedirect() {
    window.location.href = AUTH_URL;
  }

  let USER_INFO: UserData | null = null

  async function FetchDiscordData() {
    fetch(ME_URL, {mode: 'cors', credentials: 'include'})
      .then((response) => {
        if (response.status === 400) {
          return response.json().then((data) => {
            throw new Error(data.detail || 'Bad request')
          })
        }
        return response.json();
      })
      .then((data) => {
        if ('error' in data) { console.log(data) } else {
          console.log(data)
          USER_INFO = { ...data }
        }
      })
      .catch((error) => {
        console.log(error)
        // AuthRedirect()
        return [];
      });
  }

  // onMount(FetchDiscordData)

  function Echo(e: SubmitEvent) {
    const target = e.target as HTMLFormElement
    const formData = new FormData(target)
    const message = formData.get("message")
    target.reset()

    fetch(BASE_URL + "/api/echo", {
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
  <button on:click={AuthRedirect}> Authenticate </button>
  <button on:click={FetchDiscordData}> Discord Info </button>
  {#if USER_INFO}
  <div>
    
    <div class="card">
      <h1>Name: {USER_INFO.nickname}</h1>
      <h1>Admin: {USER_INFO.admin}</h1>
      <button
        on:click={async () => {
          fetch(BASE_URL + "/api/test", {mode: 'cors', credentials: 'include'})
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
    </div>
    <form action="" on:submit|preventDefault={Echo} class="flex justify-center items-center">
      <input type="text" name="message" class="h-5 text-black">
      <button class="ml-2">Send</button>
    </form>
    <ul>
      {#if USER_INFO.roles}
        {#each USER_INFO.roles as role}
          <div><span>{ROLES_DICT[role]}</span></div>
        {/each}
      {/if}
    </ul>

  </div>
  {/if}

</main>

<style>

</style>
