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
    get: () => void
}

interface Role {
    id: string,
    name: string,
    optional: boolean,
    added_by: string,
    allowed_optional: boolean
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
    boosts: number,
    roles: Role[]
}

interface TwitchStream {
    user_login: string
    added_by: string
}

interface LeftOrRight {
    name: string
    img_url: string
    added_by: string
    wins: number
}