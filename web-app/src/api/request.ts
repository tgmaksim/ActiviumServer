import { API_KEY, API_DOMAIN, CHECK_INTERNET_DOMAIN } from "../constants/app";
import type { ApiResponse } from "./base";

/**
 * Базовый адрес API.
 *
 * В отличие от Android-приложения, webSessionId не передаётся
 * вручную. Браузер автоматически отправляет cookie.
 */
const API_PREFIX = "api/v2";

/**
 * Создаёт полный URL API-запроса.
 */
function getUrl(path: string): string {
    return [
        API_DOMAIN,
        API_PREFIX,
        path,
    ].join("/");
}

/**
 * Выполняет GET-запрос к API.
 *
 * apiKey передаётся как "web".
 * webSessionId передаётся браузером автоматически
 * через cookie благодаря credentials: "include".
 *
 * @param path Путь к нужному запросу.
 * @param params Дополнительные параметры запроса в ?query.
 * @returns Десериализованный результат запроса.
 */
async function get<TRes extends ApiResponse>(
    path: string,
    params: Record<string, string | number | boolean> = {},
): Promise<TRes> {
    const url = new URL(getUrl(path));

    for (const [key, value] of Object.entries(params)) {
        url.searchParams.set(key, String(value));
    }

    const response = await fetch(url, {
        method: "GET",
        headers: {
            apiKey: API_KEY,
        },
        credentials: "include",
    });

    return parseResponse<TRes>(response);
}

/**
 * Выполняет POST-запрос к API.
 *
 * @param path Путь к нужному запросу.
 * @param params Дополнительные параметры запроса в ?query.
 * @param body Тело запроса.
 * @returns Десериализованный результат запроса.
 */
async function post<TRes extends ApiResponse>(
    path: string,
    params: Record<string, string | number | boolean> = {},
    body?: unknown,
): Promise<TRes> {
    const url = new URL(getUrl(path));

    for (const [key, value] of Object.entries(params)) {
        url.searchParams.set(key, String(value));
    }

    const response = await fetch(url, {
        method: "POST",
        headers: {
            apiKey: API_KEY,
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: body === undefined
            ? undefined
            : JSON.stringify(body),
    });

    return parseResponse<TRes>(response);
}

/**
 * Выполняет PUT-запрос к API.
 *
 * @param path Путь к нужному запросу.
 * @param params Дополнительные параметры запроса в ?query.
 * @param body Тело запроса.
 * @returns Десериализованный результат запроса.
 */
async function put<TRes extends ApiResponse>(
    path: string,
    params: Record<string, string | number | boolean> = {},
    body?: unknown,
): Promise<TRes> {
    const url = new URL(getUrl(path));

    for (const [key, value] of Object.entries(params)) {
        url.searchParams.set(key, String(value));
    }

    const response = await fetch(url, {
        method: "PUT",
        headers: {
            apiKey: API_KEY,
            "Content-Type": "application/json",
        },
        credentials: "include",
        body: body === undefined
            ? undefined
            : JSON.stringify(body),
    });

    return parseResponse<TRes>(response);
}

/**
 * Выполняет DELETE-запрос к API.
 *
 * @param path Путь к нужному запросу.
 * @param params Дополнительные параметры запроса в ?query.
 * @returns Десериализованный результат запроса.
 */
async function del<TRes extends ApiResponse>(
    path: string,
    params: Record<string, string | number | boolean> = {},
): Promise<TRes> {
    const url = new URL(getUrl(path));

    for (const [key, value] of Object.entries(params)) {
        url.searchParams.set(key, String(value));
    }

    const response = await fetch(url, {
        method: "DELETE",
        headers: {
            apiKey: API_KEY,
        },
        credentials: "include",
    });

    return parseResponse<TRes>(response);
}

/**
 * Обрабатывает HTTP-ответ и десериализует JSON.
 *
 * HTTP-ошибка отличается от ApiResponse с status=false:
 * первая означает проблему самого HTTP-запроса,
 * вторая — корректный ответ API с информацией об ошибке.
 */
async function parseResponse<TRes>(
    response: Response,
): Promise<TRes> {
    if (!response.ok) {
        throw new Error(
            `API request failed: ${response.status}`,
        );
    }

    return await response.json() as TRes;
}

/**
 * Проверяет соединение с интернетом путём попытки
 * подключения к серверу API.
 *
 * @returns true, если запрос успешно выполнен.
 */
async function checkInternet(): Promise<boolean> {
    try {
        const response = await fetch(
            CHECK_INTERNET_DOMAIN,
            {
                method: "GET",
                credentials: "include",
            },
        );

        return response.ok;
    } catch {
        return false;
    }
}

export const Request = {
    get,
    post,
    put,
    delete: del,
    checkInternet,
};
