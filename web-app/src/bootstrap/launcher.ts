import { routes } from "@/constants/routes";

const AUTHORIZED_COOKIE = "authorized";

function isAuthorized(): boolean {
    return document.cookie
        .split(";")
        .some((cookie) => {
            const [name, value] = cookie.trim().split("=");

            return (
                name === AUTHORIZED_COOKIE &&
                value === "true"
            );
        });
}

/**
 * Устанавливает состояние неавторизованного пользователя.
 *
 * Учитывает корневой путь и путь приложения, чтобы не оставить
 * действующую cookie с другим Path.
 */
export function setUnauthorized(): void {
    const basePath = import.meta.env.BASE_URL.replace(/\/+$/, "");

    const paths = new Set([
        "/",
        ...(basePath ? [basePath, `${basePath}/`] : []),
    ]);

    for (const path of paths) {
        document.cookie =
            `${AUTHORIZED_COOKIE}=false; Path=${path}; SameSite=Lax`;
    }
}

/**
 * Проверяет состояние авторизации при запуске приложения.
 */
export function launch(): null | typeof routes.loginBase {
    return isAuthorized() ? null : routes.loginBase;
}