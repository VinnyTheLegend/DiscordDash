interface UserData {
    id: bigint,
    username: string,
    global_name: string,
    avatar: string | null,
    member: boolean,
    admin: boolean,
    nickname: string | null,
    joined_at: string | null,
    roles: Array[number] | null,
    connection_time: number
}

interface User extends UserData {
    update: () => void,
    get: () => void
}