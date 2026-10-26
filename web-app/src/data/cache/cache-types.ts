export interface CacheEntry {
    childId: number;
    name: string;
    param: string;
    value: string;
}

export interface CacheKey {
    childId: number;
    name: string;
    param?: string;
}