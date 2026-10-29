import { CacheManager } from "@/data/cache/cache-manager";
import { routes } from "@/constants/routes";
import router from "@/router";
import { setUnauthorized } from "@/bootstrap/launcher";

let logoutPromise: Promise<void> | null = null;

/**
 * Завершает локальную сессию.
 *
 * Запросы к серверу не выполняются.
 * Настройки пользователя сохраняются.
 */
export function logout(): Promise<void> {
    if (logoutPromise) {
        return logoutPromise;
    }

    logoutPromise = performLogout();

    return logoutPromise;
}

async function performLogout(): Promise<void> {
    setUnauthorized();

    try {
        await CacheManager.clear();
    } finally {
        await router.replace(routes.loginBase);
    }
}