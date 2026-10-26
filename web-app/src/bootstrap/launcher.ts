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

export function launch(): null | "/login" {
    return isAuthorized() ? null : "/login";
}