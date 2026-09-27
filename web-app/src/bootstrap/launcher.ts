import routes from '../constants/routes'

const AUTHORIZED_COOKIE = "authorized";

function isAuthorized(): boolean {
    const cookies = document.cookie.split(";");

    for (const cookie of cookies) {
        const [name, ...valueParts] = cookie.trim().split("=");

        if (name === AUTHORIZED_COOKIE) {
            return valueParts.join("=") === "true";
        }
    }

    return false;
}

export function launch(): boolean {
    if (isAuthorized()) {
        return true;
    }

    window.location.replace(routes.login);

    return false;
}