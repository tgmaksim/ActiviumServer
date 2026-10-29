import { isRef, type Ref } from "vue";

import { strings } from "@/constants/strings";
import { Request } from "@/api/request";
import { Status } from "@/api/status";
import { Utilities } from "@/utils/utils";
import { logout } from "@/utils/logout";

import {
    CacheDataLoadState,
    type CacheDataLoadState as CacheDataLoadStateType,
} from "./cache-data-load-state";
import {
    LoadState,
    type LoadState as LoadStateType,
} from "./load-state";
import {
    UiText,
    type StringResourceKey,
} from "./ui-text";

type ApiError = {
    type?: string | null;
    errorMessage?: string | null;
};

type ApiResponseLike = {
    status: boolean;
    error?: ApiError | null;
};

type RequestFunction<R> = () => Promise<R>;

type SuccessMapper<R, T> = (
    response: R,
) => T | null | undefined;

type SuccessCallback<T> = (
    data: T,
) => void | Promise<void>;

type ResponseSuccessCallback<R> = (
    response: R,
) => void | Promise<void>;

type NewStateCallback = (
    state: LoadStateType<never>,
) => void;

type RequestOptions = {
    key?: string;
    cancelPrevious?: boolean;
};

function isApiResponse(value: unknown): value is ApiResponseLike {
    return (
        typeof value === "object" &&
        value !== null &&
        "status" in value &&
        typeof value.status === "boolean"
    );
}

function isCancellation(error: unknown): boolean {
    return (
        error instanceof Error &&
        (
            error.name === "AbortError" ||
            error.name === "CanceledError" ||
            error.name === "CancellationError"
        )
    );
}

export class CacheNullException extends Error {
    constructor() {
        super("Cache value is null");
        this.name = "CacheNullException";
    }
}

export default class UiViewModel {
    private readonly requestVersions = new Map<string, number>();

    private nextRequestId = 0;

    /**
     * Обычный запрос.
     */
    protected executeRequest<R extends ApiResponseLike, T>(
        state: Ref<LoadStateType<T>>,
        apiName: string,
        errorRes: StringResourceKey,
        request: RequestFunction<R>,
        mapSuccess: SuccessMapper<R, T>,
        onSuccess?: SuccessCallback<T>,
        options?: RequestOptions,
    ): Promise<void>;

    /**
     * Обычный запрос с обработчиком промежуточных состояний.
     */
    protected executeRequest<R extends ApiResponseLike, T>(
        state: Ref<LoadStateType<T>>,
        onNewState: NewStateCallback,
        apiName: string,
        errorRes: StringResourceKey,
        request: RequestFunction<R>,
        mapSuccess: SuccessMapper<R, T>,
        onSuccess?: SuccessCallback<T>,
        options?: RequestOptions,
    ): Promise<void>;

    /**
     * Облачный запрос с отдельным состоянием и хранилищем данных.
     */
    protected executeRequest<R extends ApiResponseLike, T>(
        state: Ref<CacheDataLoadStateType>,
        dataState: Ref<T | null>,
        apiName: string,
        errorRes: StringResourceKey,
        request: RequestFunction<R>,
        mapSuccess: SuccessMapper<R, T>,
        onSuccess?: ResponseSuccessCallback<R>,
        options?: RequestOptions,
    ): Promise<void>;

    /**
     * Запрос для отдельного ключа Map.
     */
    protected executeRequest<K, R extends ApiResponseLike, T>(
        state: Ref<Map<K, LoadStateType<T>>>,
        stateKey: K,
        apiName: string,
        errorRes: StringResourceKey,
        request: RequestFunction<R>,
        mapSuccess: SuccessMapper<R, T>,
        onSuccess?: SuccessCallback<T>,
        options?: RequestOptions,
    ): Promise<void>;

    /**
     * Запрос для отдельного ключа Map с обработчиком состояний.
     */
    protected executeRequest<K, R extends ApiResponseLike, T>(
        state: Ref<Map<K, LoadStateType<T>>>,
        stateKey: K,
        onNewState: NewStateCallback,
        apiName: string,
        errorRes: StringResourceKey,
        request: RequestFunction<R>,
        mapSuccess: SuccessMapper<R, T>,
        onSuccess?: SuccessCallback<T>,
        options?: RequestOptions,
    ): Promise<void>;

    protected async executeRequest(
        state: Ref<any>,
        arg2: unknown,
        arg3: unknown,
        arg4: unknown,
        arg5: unknown,
        arg6: unknown,
        arg7?: unknown,
        arg8?: unknown,
        arg9?: unknown,
    ): Promise<void> {
        let onNewState: NewStateCallback = () => {};
        let apiName: string;
        let errorRes: StringResourceKey;
        let request: RequestFunction<ApiResponseLike>;
        let mapSuccess: SuccessMapper<ApiResponseLike, unknown>;
        let onSuccess:
            | SuccessCallback<unknown>
            | ResponseSuccessCallback<ApiResponseLike>
            | undefined;
        let options: RequestOptions | undefined;

        let stateKey: unknown;
        let dataState: Ref<unknown> | undefined;

        const mapRequest = state.value instanceof Map;
        const cacheRequest = !mapRequest && isRef(arg2);

        if (cacheRequest) {
            dataState = arg2 as Ref<unknown>;
            apiName = arg3 as string;
            errorRes = arg4 as StringResourceKey;
            request = arg5 as RequestFunction<ApiResponseLike>;
            mapSuccess = arg6 as SuccessMapper<ApiResponseLike, unknown>;
            onSuccess = arg7 as
                | ResponseSuccessCallback<ApiResponseLike>
                | undefined;
            options = arg8 as RequestOptions | undefined;
        } else if (mapRequest) {
            stateKey = arg2;

            if (typeof arg3 === "function") {
                onNewState = arg3 as NewStateCallback;
                apiName = arg4 as string;
                errorRes = arg5 as StringResourceKey;
                request = arg6 as RequestFunction<ApiResponseLike>;
                mapSuccess = arg7 as SuccessMapper<ApiResponseLike, unknown>;
                onSuccess = arg8 as SuccessCallback<unknown> | undefined;
                options = arg9 as RequestOptions | undefined;
            } else {
                apiName = arg3 as string;
                errorRes = arg4 as StringResourceKey;
                request = arg5 as RequestFunction<ApiResponseLike>;
                mapSuccess = arg6 as SuccessMapper<ApiResponseLike, unknown>;
                onSuccess = arg7 as SuccessCallback<unknown> | undefined;
                options = arg8 as RequestOptions | undefined;
            }
        } else if (typeof arg2 === "function") {
            onNewState = arg2 as NewStateCallback;
            apiName = arg3 as string;
            errorRes = arg4 as StringResourceKey;
            request = arg5 as RequestFunction<ApiResponseLike>;
            mapSuccess = arg6 as SuccessMapper<ApiResponseLike, unknown>;
            onSuccess = arg7 as SuccessCallback<unknown> | undefined;
            options = arg8 as RequestOptions | undefined;
        } else {
            apiName = arg2 as string;
            errorRes = arg3 as StringResourceKey;
            request = arg4 as RequestFunction<ApiResponseLike>;
            mapSuccess = arg5 as SuccessMapper<ApiResponseLike, unknown>;
            onSuccess = arg6 as SuccessCallback<unknown> | undefined;
            options = arg7 as RequestOptions | undefined;
        }

        const requestId = ++this.nextRequestId;
        const requestKey = options?.key;

        if (requestKey && options?.cancelPrevious) {
            this.requestVersions.set(requestKey, requestId);
        }

        const isCurrentRequest = (): boolean =>
            !requestKey ||
            !options?.cancelPrevious ||
            this.requestVersions.get(requestKey) === requestId;

        const emitState = (next: LoadStateType<never>): void => {
            if (!isCurrentRequest() || cacheRequest) {
                return;
            }

            if (mapRequest) {
                const nextMap = new Map<
                    unknown,
                    LoadStateType<unknown>
                >(state.value);

                nextMap.set(
                    stateKey,
                    next as LoadStateType<unknown>,
                );

                state.value = nextMap;
            } else {
                state.value = next;
            }

            onNewState(next);
        };

        const emitError = (
            message: ReturnType<typeof UiText.dynamicString>,
        ): void => {
            if (!isCurrentRequest()) {
                return;
            }

            if (cacheRequest) {
                state.value = CacheDataLoadState.cloudError(message);
            } else {
                emitState(LoadState.error(message));
            }
        };

        const errorMessage = (
            fallback: StringResourceKey,
            error?: ApiError | null,
        ) =>
            error?.errorMessage
                ? UiText.dynamicString(error.errorMessage)
                : UiText.stringResource(fallback);

        if (cacheRequest) {
            state.value = CacheDataLoadState.cloudLoading();
        } else {
            emitState(LoadState.loading());
        }

        try {
            const response = await request();

            if (!isCurrentRequest()) {
                return;
            }

            if (!isApiResponse(response)) {
                throw new Error(`Invalid API response at ${apiName}`);
            }

            const answer = mapSuccess(response);

            if (!response.status || answer == null) {
                if (response.error) {
                    Utilities.log(
                        `API error(${response.error.type ?? "Unknown"}): ${
                            response.error.errorMessage ?? "Unknown error"
                        }`,
                    );
                }

                if (response.error?.type === "UnauthorizedError") {
                    await logout();
                    return;
                }

                emitError(errorMessage(errorRes, response.error));
                return;
            }

            if (cacheRequest) {
                dataState!.value = answer;
                state.value = CacheDataLoadState.cloudSuccess();

                await (
                    onSuccess as
                        | ResponseSuccessCallback<ApiResponseLike>
                        | undefined
                )?.(response);
            } else {
                emitState(LoadState.success(answer));

                await (
                    onSuccess as SuccessCallback<unknown> | undefined
                )?.(answer);
            }
        } catch (error: unknown) {
            if (!isCurrentRequest() || isCancellation(error)) {
                return;
            }

            let messageKey = errorRes;

            try {
                if (!(await Request.checkInternet())) {
                    messageKey = strings.errorInternet;
                } else if (!(await Status.checkHealth())) {
                    messageKey = strings.errorServer;
                } else {
                    Utilities.log(
                        error instanceof Error
                            ? error
                            : new Error(String(error)),
                        `Error at ${apiName}`,
                    );
                }
            } catch (healthError: unknown) {
                Utilities.log(
                    healthError instanceof Error
                        ? healthError
                        : new Error(String(healthError)),
                    `Health check at ${apiName}`,
                );
            }

            emitError(UiText.stringResource(messageKey));
        }
    }

    /**
     * Логически отменяет запрос с указанным ключом.
     * Устаревший результат больше не сможет обновить состояние.
     */
    protected cancelRequest(key: string): void {
        this.requestVersions.set(key, ++this.nextRequestId);
    }
}