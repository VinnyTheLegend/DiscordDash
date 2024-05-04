<script lang="ts">
  import svelteLogo from "./assets/svelte.svg";
  import viteLogo from "/vite.svg";
  import { onMount } from "svelte";

  const BASE_URL: string = "https://localhost:8000"
  const AUTH_URL: string = "https://localhost:8000/discord/authenticate";
  const URL_PARAMS = new URLSearchParams(window.location.search);
  const ME_URL: string = "https://localhost:8000/discord/me";

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

  let USER_INFO: UserData = {
    id: "",
    username: "",
    nickname: "",
    roles: [],
    isadmin: false,
  };

  async function FetchDiscordData() {
    fetch(ME_URL, {mode: 'cors', credentials: 'include'})
      .then((response) => response.json())
      .then((data) => {
        if ('error' in data) { console.log(data) } else {
          console.log(data)
          USER_INFO.id = data.user.id
          USER_INFO.username = data.user.username
          USER_INFO.nickname = data.seduction.nick
          USER_INFO.roles = []
          for(let i in data.seduction.roles) {
            if (ROLES_DICT[data.seduction.roles[i]]) {
              USER_INFO.roles = [...USER_INFO.roles, ROLES_DICT[data.seduction.roles[i]]]
            } 
          }
          USER_INFO.isadmin = data.isadmin
          console.log(USER_INFO);
        }
      })
      .catch((error) => {
        console.log(error);
        // AuthRedirect()
        return [];
      });
  }

  // onMount(FetchDiscordData)

  function Echo(e: SubmitEvent) {
    const formData = new FormData(e.target as HTMLFormElement)
    const message = formData.get("message")

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
  <h1>Name: {USER_INFO.nickname}</h1>
  <h1>Admin: {USER_INFO.isadmin}</h1>

  <div class="card">
    <button on:click={AuthRedirect}> Authenticate </button>
    <button on:click={FetchDiscordData}> Discord Info </button>
    <button
      on:click={async () => {
        fetch("https://localhost:8000/api/test", {mode: 'cors', credentials: 'include'})
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
    {#each USER_INFO.roles as role}
      <span>{role}</span>
    {/each}
  </ul>

</main>

<style>

</style>
