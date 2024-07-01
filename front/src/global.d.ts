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

interface GuildInfo {
    id: str,
    name: str,
    created_at: Date,
    member_count: number,
    role_count: number,
    voice_channel_count: number,
    text_channel_count: number,
    emoji_count: number,
    verification_level: str
}