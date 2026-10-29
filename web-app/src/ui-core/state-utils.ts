import type { Ref } from "vue";

import {
    LoadState,
    type LoadState as LoadStateType,
} from "./load-state";
import {
    CacheDataLoadState,
    type CacheDataLoadState as CacheDataLoadStateType,
} from "./cache-data-load-state";
import type { UiText } from "./ui-text";

export function isLoadError<T>(
    state: LoadState<T>,
): state is
    | Extract<LoadState<T>, { type: "error" }>
    | Extract<LoadState<T>, { type: "shownError" }> {
    return (
        state.type === "error" ||
        state.type === "shownError"
    );
}

export function setLoading<T>(
    state: Ref<LoadStateType<T>>,
): LoadStateType<never> {
    const next = LoadState.loading();
    state.value = next;
    return next;
}

export function setSuccess<T>(
    state: Ref<LoadStateType<T>>,
    data: T,
): LoadStateType<T> {
    const next = LoadState.success(data);
    state.value = next;
    return next;
}

export function setError<T>(
    state: Ref<LoadStateType<T>>,
    message: UiText,
): LoadStateType<never> {
    const next = LoadState.error(message);
    state.value = next;
    return next;
}

export function setShownError<T>(
    state: Ref<LoadStateType<T>>,
): LoadStateType<never> {
    const next = LoadState.shownError();
    state.value = next;
    return next;
}

export function setMapLoading<K, T>(
    state: Ref<Map<K, LoadStateType<T>>>,
    key: K,
): LoadStateType<never> {
    state.value = new Map(state.value).set(key, LoadState.loading());
    return LoadState.loading();
}

export function setMapSuccess<K, T>(
    state: Ref<Map<K, LoadStateType<T>>>,
    key: K,
    data: T,
): LoadStateType<T> {
    const next = LoadState.success(data);
    state.value = new Map(state.value).set(key, next);
    return next;
}

export function setMapError<K, T>(
    state: Ref<Map<K, LoadStateType<T>>>,
    key: K,
    message: UiText,
): LoadStateType<never> {
    const next = LoadState.error(message);
    state.value = new Map(state.value).set(key, next);
    return next;
}

export function resetMapSuccess<K, T>(
    state: Ref<Map<K, LoadStateType<T>>>,
    key: K,
): void {
    const next = new Map(state.value);
    next.delete(key);
    state.value = next;
}

export function setCacheLoading(
    state: Ref<CacheDataLoadStateType>,
): CacheDataLoadStateType {
    const next = CacheDataLoadState.cacheLoading();
    state.value = next;
    return next;
}

export function setCacheSuccess(
    state: Ref<CacheDataLoadStateType>,
): CacheDataLoadStateType {
    const next = CacheDataLoadState.cacheSuccess();
    state.value = next;
    return next;
}

export function setCacheError(
    state: Ref<CacheDataLoadStateType>,
    message: UiText,
): CacheDataLoadStateType {
    const next = CacheDataLoadState.cacheError(message);
    state.value = next;
    return next;
}

export function setCloudLoading(
    state: Ref<CacheDataLoadStateType>,
): CacheDataLoadStateType {
    const next = CacheDataLoadState.cloudLoading();
    state.value = next;
    return next;
}

export function setCloudSuccess(
    state: Ref<CacheDataLoadStateType>,
): CacheDataLoadStateType {
    const next = CacheDataLoadState.cloudSuccess();
    state.value = next;
    return next;
}

export function setCloudError(
    state: Ref<CacheDataLoadStateType>,
    message: UiText,
): CacheDataLoadStateType {
    const next = CacheDataLoadState.cloudError(message);
    state.value = next;
    return next;
}

export function setShownCacheError(
    state: Ref<CacheDataLoadStateType>,
): CacheDataLoadStateType {
    const next = CacheDataLoadState.shownError();
    state.value = next;
    return next;
}