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
    "591687458819932172": {name: "Veteran", color: "yellow"},
    "591687038902992928": {name: "Member", color: "blue"},
    "1222684351054221312":{name: "Twitch Notifications", color: "#47003C"},
    "850013094758842400": {name: "Drops", color: "var(--accent)"},
    "591684990811635724": {name: "Everyone", color: "var(--accent)"}

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