interface UserData {
    id: string,
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

interface GuildInfo {
    id: string,
    name: string,
    created_at: Date,
    member_count: number,
    role_count: number,
    voice_channel_count: number,
    text_channel_count: number,
    emoji_count: number,
    verification_level: string,
    boosts: number
}

interface Member {
    id: string,
    username: string,
    global_name: string,
    nickname: string,
    avatar: string,
    connection_time: number
    roles: {id: string, name: string}[]
}