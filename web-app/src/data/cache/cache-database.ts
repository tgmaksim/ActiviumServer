import Dexie, { type Table } from "dexie";

import type { CacheEntry } from "./cache-types";

class CacheDatabase extends Dexie {
    dnevnikCache!: Table<CacheEntry, [number, string, string]>;

    constructor() {
        super("activium-cache");

        this.version(1).stores({
            dnevnikCache: "[childId+name+param]",
        });
    }
}

export const cacheDatabase = new CacheDatabase();