interface UserData {
    id: String,
    username: String,
    global_name: String,
    avatar: String,
    token: String,
    expires_in: String,
    refresh_token: String,
    expires_at: String,
    member: Boolean,
    is_admin: Boolean,
    nickname: String | null,
    joined_at: String | null,
    roles: Array[Number] | null
}