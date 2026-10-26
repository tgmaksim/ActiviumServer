import { cacheDatabase } from "./cache-database";
import type { CacheEntry, CacheKey } from "./cache-types";

export const CacheManager = {
    async writeDnevnikCache(
        childId: number,
        name: string,
        value: string,
        param = "",
    ): Promise<void> {
        const entry: CacheEntry = {
            childId,
            name,
            param,
            value,
        };

        await cacheDatabase.dnevnikCache.put(entry);
    },

    async read(
        childId: number,
        name: string,
        param = "",
    ): Promise<CacheEntry | undefined> {
        return cacheDatabase.dnevnikCache.get([
            childId,
            name,
            param,
        ]);
    },

    async remove({
        childId,
        name,
        param = "",
    }: CacheKey): Promise<void> {
        await cacheDatabase.dnevnikCache.delete([
            childId,
            name,
            param,
        ]);
    },

    async clear(): Promise<void> {
        await cacheDatabase.dnevnikCache.clear();
    },
};