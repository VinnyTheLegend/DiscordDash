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

export function fetch_members() {
    fetch(URLS.BASE_URL+'/api/guild/members', { mode: "cors", credentials: "include" })
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
        let members_new = data
        members.set(members_new)
    })
    .catch((error) => {
        console.log(error);
        return [];
    });
}

export function get_member(id: string, members_list: UserData[]): UserData | void {
    members_list.forEach(member => {
        if (member.id === id) {
            console.log(member.nickname)
            return member
        }
    });
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