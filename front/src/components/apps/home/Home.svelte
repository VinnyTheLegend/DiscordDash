<script lang="ts">
    import { URLS } from "../../../utils";

    export let USER: User;
    let guild_info: GuildInfo

    fetch(URLS.BASE_URL+'/api/guild', { mode: "cors", credentials: "include" })
        .then((response) => {
          if (response.status === 400) {
            return response.json().then((data) => {
              throw new Error(data.detail || "Bad request");
            });
          }
          return response.json();
        })
        .then((data: GuildInfo) => {
            data.created_at = new Date(data.created_at)
            guild_info = data
            console.log(guild_info)
        })
        .catch((error) => {
            console.log(error);
            return [];
        });

</script>

<main class="size-full flex justify-evenly items-center">
    <div class="">
        <h4 class="text-center">Server</h4>
        <div class="w-[300px] h-[500px] border-2 border-border rounded">
            <div class="h-1/3 border-b border-border">
                <div class="w-full flex px-2">
                    <h1 class="text-left w-1/2">Creation Date:</h1>
                    <h1 class="text-right w-1/2">{guild_info?.created_at.toDateString() || ""}</h1>
                </div>
                <div class="w-full flex px-2">
                    <h1 class="text-left w-1/2">Members:</h1>
                    <h1 class="text-right w-1/2">{guild_info?.member_count || ""}</h1>
                </div>
                <div class="w-full flex px-2">
                    <h1 class="text-left w-1/2">Roles:</h1>
                    <h1 class="text-right w-1/2">{guild_info?.role_count || ""}</h1>
                </div>
                <div class="w-full flex px-2">
                    <h1 class="text-left w-1/2">Text Channels:</h1>
                    <h1 class="text-right w-1/2">{guild_info?.text_channel_count || ""}</h1>
                </div>
                <div class="w-full flex px-2">
                    <h1 class="text-left w-1/2">Voice Channels:</h1>
                    <h1 class="text-right w-1/2">{guild_info?.voice_channel_count || ""}</h1>
                </div>
                <div class="w-full flex px-2">
                    <h1 class="text-left w-1/2">Boosts:</h1>
                    <h1 class="text-right w-1/2">{guild_info?.boosts || ""}</h1>
                </div>
            </div>
            <div class="h-2/3"></div>
        </div>
    </div>
    <div>
        <h1 class="text-center">Recent Logs</h1>    
        <div class="w-[750px] h-[500px] border-2 border-border rounded">
        
        </div>
    </div>
    <div>
        <h1 class="text-center">{USER?.username || "User"}</h1>
        <div class="w-[300px] h-[500px] border-2 border-border rounded">
        
        </div>
    </div>
</main>

<style>

</style>
