import { writable } from 'svelte/store';
import type { Writable } from 'svelte/store';

export const members: Writable<UserData[]> = writable([]);
export const guild_info: Writable<GuildInfo> = writable();
