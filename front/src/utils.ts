import { members, guild_info } from "./stores";

export const BASE_URL = import.meta.env.VITE_BACK_URL;

export const URLS = {
    BASE_URL: BASE_URL,
    AUTH_URL: `${BASE_URL}/discord/authenticate`,
    USER_URL: `${BASE_URL}/discord/user`,
    FRONT_URL: import.meta.env.VITE_FRONT_URL,
    INVITE_URL: 'https://discord.gg/zcrX9ntken'
}

export const role_colors: { [key: string]: {color: string} } = {
    "Warlord": {color: "red"},
    "General": {color: "green"},
    "Veteran Member": {color: "darkorange"},
    "Member": {color: "blue"},
    "Twitch Notifications": {color:"#47003C"},
    "Drops": {color: "#47003C"},
    "Valheim": {color: "#47003C"}

}

export function echo(message: string) {
    fetch(URLS.BASE_URL + "/api/echo", {
        mode: "cors",
        credentials: "include",
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: message }),
    }).then((res) => {
        console.log("Echo response", res);
    });
}

export async function fetch_members(skip: number = 0, limit: number = 100): Promise<UserData[] | void> {
    let member_url = new URL(URLS.BASE_URL+'/api/guild/members')
    member_url.searchParams.set('skip', skip.toString())
    member_url.searchParams.set('limit', limit.toString())


    return fetch(member_url, { mode: "cors", credentials: "include" })
    .then((response) => {
      if (response.status === 400) {
        return response.json().then((data) => {
          throw new Error(data.detail || "Bad request");
        });
      }
      return response.json();
    })
    .then((data: UserData[]) => {
        console.log(data)
        return data
    })
    .catch((error) => {
        console.log(error);
        return;
    });
}

export async function update_member_store() {
    let new_members_value: UserData[] = []
    let fetched_members = await fetch_members()
    if (!fetched_members) return
    new_members_value.push(...fetched_members)
    let toskip = 100
    while (fetched_members && fetched_members.length >= 100) {
        fetched_members = await fetch_members(toskip)
        toskip = toskip + 100
        if (fetched_members) new_members_value.push(...fetched_members)
    }
    members.set(new_members_value)
}


export function fetch_guild() {
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
        guild_info.set(data)
        console.log(data)
    })
    .catch((error) => {
        console.log(error);
        return [];
    });
}

export function get_member(id: string, members_value: UserData[]): string {
    const member = members_value.find(member => member.id === id);
    if (member) {
        console.log(member.nickname);
        return member.nickname || member.global_name;
    }
    return 'Unknown'
}