import type {
    ApiBase,
    ApiResponse,
} from "./base";

import { Request } from "./request";

/**
 * Результат запроса данных о последней версии приложения.
 *
 * @property latestVersionNumber Последняя доступная версия (номер сборки) приложения.
 * @property latestVersionString Последняя доступная версия приложения.
 * @property date Дата выпуска последней доступной версии приложения.
 * @property versionStatusId Числовой статус новой версии, означающий важность обновления.
 * @property versionStatus Статус новой версии, означающий важность обновления.
 * @property info Дополнительная информация о версии.
 * @property updateLogs Изменения в последней версии приложения, которые можно показать пользователю.
 */
export interface VersionsResult extends ApiBase {
    classId: 0x43;
    latestVersionNumber: number;
    latestVersionString: string;
    date: string;
    versionStatusId: number;
    versionStatus: string;
    info: string | null;
    updateLogs: string;
}

/**
 * Ответ на запрос данных о последней версии приложения.
 */
export interface VersionsApiResponse
    extends ApiResponse<VersionsResult | null> {
    classId: 0x44 | 0x2;
}

/**
 * Ответ на запрос проверки работоспособности сервера.
 */
export interface HealthApiResponse
    extends ApiResponse<null> {
    classId: 0x5 | 0x2;
}

/**
 * Информационное сообщение.
 *
 * @property title Заголовок сообщения.
 * @property text Текст сообщения.
 */
export interface Message extends ApiBase {
    classId: 0x40;
    title: string;
    text: string;
}

/**
 * Результат запроса получения информационных сообщений.
 *
 * @property messages Информационные сообщения для пользователя, если есть.
 */
export interface InformationResult extends ApiBase {
    classId: 0x41;
    messages: Message[];
}

/**
 * Ответ на запрос получения информационных сообщений.
 */
export interface InformationApiResponse
    extends ApiResponse<InformationResult | null> {
    classId: 0x42 | 0x2;
}

const PATH_STATUS = "status";
const PATH_CHECK_VERSION = "checkVersion";
const PATH_HEALTH = "health";
const PATH_CHECK_INFO_NOTIFICATIONS =
    "checkInfoNotifications";

const CHECK_VERSION_VERSION = 1;
const HEALTH_VERSION = 0;
const CHECK_INFO_NOTIFICATIONS_VERSION = 0;

/**
 * Получение данных о последней доступной версии приложения.
 *
 * @param versionCode Текущий номер сборки приложения.
 */
async function checkVersion(
    versionCode: number,
): Promise<VersionsApiResponse> {
    return Request.get<VersionsApiResponse>(
        [
            PATH_STATUS,
            PATH_CHECK_VERSION,
            CHECK_VERSION_VERSION,
        ].join("/"),
        {
            versionNumber: versionCode,
        },
    );
}

/**
 * Проверка работоспособности сервера.
 */
async function health(): Promise<HealthApiResponse> {
    return Request.get<HealthApiResponse>(
        [
            PATH_STATUS,
            PATH_HEALTH,
            HEALTH_VERSION,
        ].join("/"),
    );
}

/**
 * Проверка наличия и получение коротких
 * оповещений для пользователя.
 */
async function checkInfoNotifications(): Promise<InformationApiResponse> {
    return Request.get<InformationApiResponse>(
        [
            PATH_STATUS,
            PATH_CHECK_INFO_NOTIFICATIONS,
            CHECK_INFO_NOTIFICATIONS_VERSION,
        ].join("/"),
    );
}

/**
 * Проверка работоспособности сервера.
 */
async function checkHealth(): Promise<boolean> {
    try {
        return (await health()).status;
    } catch {
        return false;
    }
}

/**
 * API-запросы группы status.
 */
export const Status = {
    checkVersion,
    health,
    checkInfoNotifications,
    checkHealth,
};
