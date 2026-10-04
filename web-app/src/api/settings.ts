import type {
    ApiBase,
    ApiResponse,
} from "./base";

import { Request } from "./request";

/**
 * Ребенок.
 *
 * @property childId Идентификатор ребенка, который необходим для выбора активного.
 * @property name Имя ребенка для показа в клиенте.
 */
export interface Child extends ApiBase {
    classId: 0x21;
    childId: number;
    name: string;
}

/**
 * Результат запроса получения своих детей.
 *
 * @property children Список детей, привязанных к пользователю сессии.
 * @property activeChildId Идентификатор активного ребенка.
 */
export interface ChildrenResult extends ApiBase {
    classId: 0x22;
    children: Child[];
    activeChildId: number;
}

/**
 * Ответ на запрос получения своих детей.
 */
export interface ChildrenApiResponse
    extends ApiResponse<ChildrenResult | null> {
    classId: 0x23 | 0x2;
}

/**
 * Ответ на запрос изменения активного ребенка родителя.
 */
export interface SwitchActiveChildApiResponse
    extends ApiResponse<ChildrenResult | null> {
    classId: 0x24 | 0x2;
}

/**
 * Результат запроса получения статуса настройки уведомлений
 * о новых оценках.
 *
 * @property status Статус функции уведомлений о новых оценках.
 */
export interface StatusMarksNotificationsResult extends ApiBase {
    classId: 0x25;
    status: boolean;
}

/**
 * Ответ на запрос получения статуса настройки уведомлений
 * о новых оценках.
 */
export interface StatusMarksNotificationsApiResponse
    extends ApiResponse<StatusMarksNotificationsResult | null> {
    classId: 0x26 | 0x2;
}

/**
 * Ответ на запрос изменения настройки уведомлений
 * о новых оценках.
 *
 * answer всегда равен null.
 */
export interface SwitchMarksNotificationsApiResponse
    extends ApiResponse<null> {
    classId: 0x27 | 0x2;
}

/**
 * Ответ на запрос обновления Firebase-токена
 * для работы уведомлений.
 *
 * answer всегда равен null.
 */
export interface UpdateFirebaseApiResponse
    extends ApiResponse<null> {
    classId: 0x28 | 0x2;
}

/**
 * Результат запроса получения статуса настройки уведомлений
 * о внеурочных занятиях.
 *
 * @property status Статус функции уведомлений о внеурочных занятиях.
 */
export interface StatusEANotificationsResult extends ApiBase {
    classId: 0x3B;
    status: boolean;
}

/**
 * Ответ на запрос получения статуса настройки уведомлений
 * о внеурочных занятиях.
 */
export interface StatusEANotificationsApiResponse
    extends ApiResponse<StatusEANotificationsResult | null> {
    classId: 0x3C | 0x2;
}

/**
 * Ответ на запрос изменения настройки уведомлений
 * о внеурочных занятиях.
 *
 * answer всегда равен null.
 */
export interface SwitchEANotificationsApiResponse
    extends ApiResponse<null> {
    classId: 0x3D | 0x2;
}

/**
 * Результат запроса получения параметров реферальной программы
 * для пользователя.
 *
 * @property meReferralName Имя пользователя, который пригласил.
 * @property referralsCount Количество приглашенных пользователей.
 * @property isParent Является ли пользователь родителем.
 * @property countActiveRelatives Количество активных родственников.
 * @property countRelatives Количество родственников.
 * @property referralUrl Реферальная ссылка для приглашения.
 */
export interface ReferralParamsResult extends ApiBase {
    classId: 0x5F;
    meReferralName: string | null;
    referralsCount: number;
    isParent: boolean;
    countActiveRelatives: number;
    countRelatives: number;
    referralUrl: string;
}

/**
 * Ответ на запрос получения параметров реферальной программы
 * для пользователя.
 */
export interface ReferralParamsApiResponse
    extends ApiResponse<ReferralParamsResult | null> {
    classId: 0x60 | 0x2;
}

/**
 * Ответ на запрос скрытия уведомлений
 * об определенном внеурочном занятии.
 *
 * answer всегда равен null.
 */
export interface HideExtracurricularActivityApiResponse
    extends ApiResponse<null> {
    classId: 0x65 | 0x2;
}

const PATH_PREFIX = "settings";

const PATH_CHILDREN = "getChildren";
const PATH_ACTIVE_CHILD = "setActiveChild";
const PATH_MARKS_NOTIFICATIONS = "getStatusMarksNotifications";
const PATH_SWITCH_MARKS_NOTIFICATIONS = "switchMarksNotifications";
const PATH_UPDATE_FIREBASE = "updateFirebase";
const PATH_EA_NOTIFICATIONS = "getStatusEANotifications";
const PATH_SWITCH_EA_NOTIFICATIONS = "switchEANotifications";
const PATH_REFERRAL_PARAMS = "getReferralParams";
const PATH_HIDE_EXTRACURRICULAR_ACTIVITY =
    "hideExtracurricularActivity";

const CHILDREN_VERSION = 0;
const ACTIVE_CHILD_VERSION = 0;
const MARKS_NOTIFICATIONS_VERSION = 0;
const SWITCH_MARKS_NOTIFICATIONS_VERSION = 0;
const UPDATE_FIREBASE_VERSION = 0;
const EA_NOTIFICATIONS_VERSION = 0;
const SWITCH_EA_NOTIFICATIONS_VERSION = 0;
const REFERRAL_PARAMS_VERSION = 1;
const HIDE_EXTRACURRICULAR_ACTIVITY_VERSION = 0;

/**
 * Получение списка детей, привязанных к пользователю сессии,
 * и активного ребенка.
 */
async function getChildren(): Promise<ChildrenApiResponse> {
    return Request.get<ChildrenApiResponse>(
        [
            PATH_PREFIX,
            PATH_CHILDREN,
            CHILDREN_VERSION,
        ].join("/"),
    );
}

/**
 * Выбор активного ребенка родителя,
 * с которым ведется взаимодействие.
 *
 * @param childId Идентификатор ребенка, полученный запросом.
 */
async function setActiveChild(
    childId: number,
): Promise<SwitchActiveChildApiResponse> {
    return Request.put<SwitchActiveChildApiResponse>(
        [
            PATH_PREFIX,
            PATH_ACTIVE_CHILD,
            ACTIVE_CHILD_VERSION,
        ].join("/"),
        {
            childId,
        },
    );
}

/**
 * Получение статуса настройки уведомлений
 * о новых оценках для активного ребенка.
 */
async function getStatusMarksNotifications(): Promise<StatusMarksNotificationsApiResponse> {
    return Request.get<StatusMarksNotificationsApiResponse>(
        [
            PATH_PREFIX,
            PATH_MARKS_NOTIFICATIONS,
            MARKS_NOTIFICATIONS_VERSION,
        ].join("/"),
    );
}

/**
 * Включение или выключение уведомлений
 * о новых оценках для активного ребенка.
 *
 * @param status Новый статус настройки.
 */
async function switchMarksNotifications(
    status: boolean,
): Promise<SwitchMarksNotificationsApiResponse> {
    return Request.put<SwitchMarksNotificationsApiResponse>(
        [
            PATH_PREFIX,
            PATH_SWITCH_MARKS_NOTIFICATIONS,
            SWITCH_MARKS_NOTIFICATIONS_VERSION,
        ].join("/"),
        {
            status,
        },
    );
}

/**
 * Установление или обновление сохраненного Firebase-токена
 * для уведомлений.
 *
 * @param firebaseToken Firebase-токен для отправки уведомлений клиенту.
 */
async function updateFirebase(
    firebaseToken: string,
): Promise<UpdateFirebaseApiResponse> {
    return Request.put<UpdateFirebaseApiResponse>(
        [
            PATH_PREFIX,
            PATH_UPDATE_FIREBASE,
            UPDATE_FIREBASE_VERSION,
        ].join("/"),
        {
            firebaseToken,
        },
    );
}

/**
 * Получение статуса настройки уведомлений
 * о внеурочных занятиях для активного ребенка.
 */
async function getStatusEANotifications(): Promise<StatusEANotificationsApiResponse> {
    return Request.get<StatusEANotificationsApiResponse>(
        [
            PATH_PREFIX,
            PATH_EA_NOTIFICATIONS,
            EA_NOTIFICATIONS_VERSION,
        ].join("/"),
    );
}

/**
 * Включение или выключение уведомлений
 * о внеурочных занятиях для активного ребенка.
 *
 * @param status Новый статус настройки.
 */
async function switchEANotifications(
    status: boolean,
): Promise<SwitchEANotificationsApiResponse> {
    return Request.put<SwitchEANotificationsApiResponse>(
        [
            PATH_PREFIX,
            PATH_SWITCH_EA_NOTIFICATIONS,
            SWITCH_EA_NOTIFICATIONS_VERSION,
        ].join("/"),
        {
            status,
        },
    );
}

/**
 * Получение количества приглашенных пользователей,
 * ссылки для приглашения и имени пользователя,
 * который пригласил пользователя.
 */
async function getReferralParams(): Promise<ReferralParamsApiResponse> {
    return Request.get<ReferralParamsApiResponse>(
        [
            PATH_PREFIX,
            PATH_REFERRAL_PARAMS,
            REFERRAL_PARAMS_VERSION,
        ].join("/"),
    );
}

/**
 * Скрытие уведомлений с напоминанием
 * об определенном внеурочном занятии.
 *
 * @param childId Идентификатор ребенка.
 * @param subject Предмет внеурочного занятия.
 * @param place Место проведения.
 */
async function hideExtracurricularActivity(
    childId: number,
    subject: string,
    place: string,
): Promise<HideExtracurricularActivityApiResponse> {
    return Request.put<HideExtracurricularActivityApiResponse>(
        [
            PATH_PREFIX,
            PATH_HIDE_EXTRACURRICULAR_ACTIVITY,
            HIDE_EXTRACURRICULAR_ACTIVITY_VERSION,
        ].join("/"),
        {
            childId,
            subject,
            place,
        },
    );
}

/**
 * API-запросы группы settings.
 */
export const Settings = {
    getChildren,
    setActiveChild,
    getStatusMarksNotifications,
    switchMarksNotifications,
    updateFirebase,
    getStatusEANotifications,
    switchEANotifications,
    getReferralParams,
    hideExtracurricularActivity,
};