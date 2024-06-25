interface UserData {
    id: str,
    username: string,
    global_name: string,
    avatar: string | null,
    member: boolean,
    admin: boolean,
    nickname: string | null,
    joined_at: string | null,
    roles: string[] | null,
    connection_time: number
}

interface User extends UserData {
    update: () => void,
    get: () => void
}