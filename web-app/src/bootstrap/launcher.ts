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
    const basePath = routes.home.replace(/\/+$/, "");

    document.cookie = `${AUTHORIZED_COOKIE}=false; Path=${basePath}; SameSite=Lax; max-age=` + (90 * 24 * 60 * 60);
}

/**
 * Проверяет состояние авторизации при запуске приложения.
 */
export function launch(): null | typeof routes.loginBase {
    return isAuthorized() ? null : routes.loginBase;
}