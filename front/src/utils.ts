import { members, guild_info } from "./stores";

export const BASE_URL: string = "https://localhost:8000";

export const URLS = {
    BASE_URL: BASE_URL,
    AUTH_URL: BASE_URL + "/discord/authenticate",
    USER_URL: BASE_URL + "/discord/user",
    FRONT_URL: "https://localhost:5173"
}

export const ROLES_DICT: { [key: string]: {name: string, color: string} } = {
    "591686220996935691": {name: "Warlord", color: "red"},
    "591686523142012948": {name: "General", color: "green"},
    "591687458819932172": {name: "Veteran", color: "darkorange"},
    "591687038902992928": {name: "Member", color: "blue"},
    "1222684351054221312":{name: "Twitch Notifications", color: "#47003C"},
    "850013094758842400": {name: "Drops", color: "#47003C"}

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
    console.log('new members:', fetched_members)
    if (!fetched_members) return
    new_members_value.push(...fetched_members)
    while (fetched_members && fetched_members.length >= 100) {
        fetched_members = await fetch_members()
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