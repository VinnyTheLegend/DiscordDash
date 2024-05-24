<script lang="ts">
  import NavBar from "./components/NavBar.svelte";
  import {URLS, ROLES_DICT} from './utils'

  let USER: User = {
    get: function(this: User) {
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
          console.log(data);
          Object.assign(this, data)
          USER=USER
        }
      })
      .catch((error) => {
        console.log(error);
        // AuthRedirect()
        return [];
      });
    },
    
    update: function(this: User) {
      fetch(URLS.USER_URL + '/update', { mode: "cors", credentials: "include" })
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
          console.log(data);
          Object.assign(this, data)
          USER=USER
        }
      })
      .catch((error) => {
        console.log(error);
        // AuthRedirect()
        return [];
      });
    }
  }

</script>

<main>
  <NavBar {USER} />
</main>

<style>
</style>
