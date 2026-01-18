<script lang="ts">
  import Header from "./components/Header.svelte";
  import SideBar from "./components/SideBar.svelte";
  import { update_member_store, URLS } from "./utils";
  import { Button } from "$lib/components/ui/button";
  import AppSwitch from "./components/AppSwitch.svelte";
  import { Toaster } from "$lib/components/ui/sonner";
  import { fetch_guild, } from "./utils";
  
  console.log('here')
  console.log('env', import.meta.env.VITE_BACK_URL)
  console.log('env', import.meta.env.VITE_FRONT_URL)

  let USER: User = {
    id: "",
    username: '',
    global_name: '',
    avatar: '',
    member: false,
    admin: false,
    nickname: null,
    joined_at: null,
    roles: null,
    connection_time: 0,
    muted_time: 0,
    deafened_time: 0,
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
            window.location.href = `${URLS.BASE_URL}/logout`
            console.log(data);
          } else {
            console.log(data);
            Object.assign(this, data);
            USER = USER;
          }
        })
        .catch((error) => {
          console.log(error);
          window.location.href = `${URLS.BASE_URL}/logout`
          // AuthRedirect()
          return [];
        });
    }
  };

  let auth;
  document.cookie === "" ? (auth = false) : (auth = true);
  if (auth) {
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
          window.location.href = `${URLS.BASE_URL}/logout`;
          console.log(data);
        } else {
          console.log(data);
          Object.assign(USER, data);
          USER = USER;
          if (USER.member) {
            fetch_guild();
            update_member_store();
          }
        }
      })
      .catch((error) => {
        console.log(error);
        window.location.href = `${URLS.BASE_URL}/logout`;
        return [];
      });
  }
  
  const apps = ['home', 'twitch', 'roles', 'leftorright']
  let current_app: string = "home"
  let redirect = sessionStorage.getItem('redirect');
  if (redirect) {
      let path = redirect.replace('/', '');
      if (apps.includes(path)) {
          current_app = path;
          history.pushState({}, '', '/' + current_app);
      }
      sessionStorage.removeItem('redirect');
  } else {
      let pathname = window.location.pathname.replace('/', '')
      if (apps.includes(pathname)) {
        current_app = pathname
      } else if (pathname == 'invite') {
        window.location.href = 'https://discord.gg/zcrX9ntken'
        console.log('https://discord.gg/zcrX9ntken')
      } else if (pathname != '') {
        window.location.pathname = ''
      }
  }
  async function changeApp(event: CustomEvent<string>) {
    current_app = event.detail;
    if (current_app !== 'home') {
        history.pushState({}, '', '/' + current_app);
    } else {
        history.pushState({}, '', '/');
    }
  }
  
  let sidebar_shown = false
  function toggleSidebar(event: CustomEvent<boolean>) {
    sidebar_shown = event.detail
  }

</script>

<main class="h-screen w-screen flex flex-col relative">
  {#if auth && USER.id}
    <Header {USER} on:toggleSidebar={toggleSidebar}/>
    <Toaster/>
    {#if USER.member}
      <div class="flex-grow flex min-h-0 min-w-0">
        <SideBar {sidebar_shown} on:changeApp={changeApp} {USER}/>
        <AppSwitch {current_app} {USER}/>
      </div>
    {:else if USER.member === false}
      <div class="flex-grow flex min-h-0 min-w-0 justify-center items-center">
        <div>Not a member</div>
      </div>
    {/if}
  {:else if auth}
    <div class="flex h-full justify-end"></div>
  {:else}
    <div class="flex h-full justify-center items-center">
      <Button on:click={() => {window.location.href = URLS.AUTH_URL}}>Authenticate</Button>
    </div>
  {/if}
</main>

<style>
  main {
    background: rgb(52,0,47);
    background: linear-gradient(0deg, rgba(52,0,47,1) 0%, rgba(0,0,0,1) 58%);
  }
</style>
