<script lang="ts">
    import { URLS } from "../../utils";

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

<main class="w-[300px] h-[500px] border-2 border-border rounded">
    <div class="border-b border-border">
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
    <div class="">
        
    </div>

</main>

<style>
h1 {
    text-shadow: -1px -1px 0 #47003C, 1px -1px 0 #47003C, -1px 1px 0 #47003C, 1px 1px 0 #47003C;
}
</style>
