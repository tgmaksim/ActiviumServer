import { CacheManager } from "@/data/cache/cache-manager";
import { routes } from "@/constants/routes";
import router from "@/router";
import { setUnauthorized } from "@/bootstrap/launcher";

/**
 * Завершает локальную сессию Активиум.
 *
 * Запросы к серверу не выполняются.
 * Настройки пользователя сохраняются.
 */
export async function logout(): Promise<void> {
    setUnauthorized();

    try {
        await CacheManager.clear();
    } finally {
        await router.replace(routes.loginBase);
    }
}