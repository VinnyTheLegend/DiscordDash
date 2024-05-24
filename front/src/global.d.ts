interface UserData {
    id?: String,
    username?: String,
    global_name?: String,
    avatar?: String,
    member?: Boolean,
    admin?: Boolean,
    nickname?: String | null,
    joined_at?: String | null,
    roles?: Array[Number] | null
}

interface User extends UserData {
    update: () => void,
    get: () => void
}