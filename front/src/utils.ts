export const BASE_URL: string = "https://localhost:8000";

export const URLS = {
    BASE_URL: BASE_URL,
    AUTH_URL: BASE_URL + "/discord/authenticate",
    USER_URL: BASE_URL + "/discord/user",
    FRONT_URL: "https://localhost:5173"
}

export const ROLES_DICT: { [key: string]: string } = {
    "591686220996935691": "Warlord",
    "591686523142012948": "General",
    "591687458819932172": "Veteran",
    "591687038902992928": "Member",
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