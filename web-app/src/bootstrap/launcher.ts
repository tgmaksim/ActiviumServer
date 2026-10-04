import {
    APP_VERSION,
    APP_VERSION_STORAGE_KEY,
    APP_VERSION_CODE,
    APP_VERSION_CODE_STORAGE_KEY,
} from "../constants/app";

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

export function launch(): "/" | "/login" {
    localStorage.setItem(
        APP_VERSION_STORAGE_KEY,
        APP_VERSION,
    );
    localStorage.setItem(
        APP_VERSION_CODE_STORAGE_KEY,
        APP_VERSION_CODE.toString(),
    );

    return isAuthorized() ? "/" : "/login";
}