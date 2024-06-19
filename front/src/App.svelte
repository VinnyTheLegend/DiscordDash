<script lang="ts">
  import Header from "./components/Header.svelte";
  import { URLS } from "./utils";

  let USER: User = {
    id: BigInt(0),
    username: '',
    global_name: '',
    avatar: '',
    member: false,
    admin: false,
    nickname: null,
    joined_at: null,
    roles: null,
    connection_time: 0,
    get: function (this: User) {
      fetch(URLS.USER_URL, { mode: "cors", credentials: "include" })
        .then((response) => {
          if (response.status === 400) {
            return response.json().then((data) => {
              throw new Error(data.detail || "Bad request");
            });
          }
          return response.json();
        })
        .then((data: UserData) => {
          if ("error" in data) {
            console.log(data);
          } else {
            data.id = BigInt(data.id)
            console.log(data);
            Object.assign(this, data);
            USER = USER;
          }
        })
        .catch((error) => {
          console.log(error);
          // AuthRedirect()
          return [];
        });
    },

    update: function (this: User) {
      fetch(URLS.USER_URL + "/update", { mode: "cors", credentials: "include" })
        .then((response) => {
          if (response.status === 400) {
            return response.json().then((data) => {
              throw new Error(data.detail || "Bad request");
            });
          }
          return response.json();
        })
        .then((data: UserData) => {
          if ("error" in data) {
            console.log(data);
          } else {
            data.id = BigInt(data.id)
            console.log(data);
            Object.assign(this, data);
            USER = USER;
          }
        })
        .catch((error) => {
          console.log(error);
          // AuthRedirect()
          return [];
        });
    },
  };

  let auth;
  document.cookie === "" ? (auth = false) : (auth = true);
  if (auth) {
    USER.get();
  }
</script>

<main class="h-full w-full">
  {#if auth && USER.member}
    <Header {USER} />
  {:else if auth}
    <div class="flex h-full justify-center items-center">
      <div>Not a member</div>
    </div>
  {:else}
    <div class="flex h-full justify-center items-center">
      <button
        on:click={() => {
          window.location.href = URLS.AUTH_URL;
        }}
      >
        Authenticate
      </button>
    </div>
  {/if}
</main>

<style>
  main {
    background: rgb(52,0,47);
    background: linear-gradient(0deg, rgba(52,0,47,1) 0%, rgba(0,0,0,1) 58%);
  }
</style>
