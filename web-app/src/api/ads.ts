import type {
    ApiBase,
    ApiResponse,
} from "./base";

import { Request } from "./request";

/**
 * Рекламное объявление.
 */
export interface Ad extends ApiBase {
    classId: 0x61;
    adId: number;
    title: string;
    text: string;
    imageUrl: string;
    url: string;
}

/**
 * Результат запроса получения рекламного объявления.
 */
export interface AdResult extends ApiBase {
    classId: 0x62;
    ad: Ad | null;
}

/**
 * Ответ на запрос получения рекламного объявления.
 */
export interface AdApiResponse
    extends ApiResponse<AdResult | null> {
    classId: 0x63 | 0x2;
}

/**
 * Ответ на запрос клика на рекламу.
 */
export interface ClickAdApiResponse
    extends ApiResponse<null> {
    classId: 0x64 | 0x2;
}

const PATH_ADS = "ads";
const PATH_CHECK_ACCESSIBLE_AD = "checkAccessibleAd";
const PATH_CLICK_AD = "clickAd";

const CHECK_ACCESSIBLE_AD_VERSION = 0;
const CLICK_AD_VERSION = 0;

/**
 * Проверка наличия и получение рекламного объявления.
 */
async function checkAccessibleAd(): Promise<AdApiResponse> {
    return Request.post<AdApiResponse>(
        [
            PATH_ADS,
            PATH_CHECK_ACCESSIBLE_AD,
            CHECK_ACCESSIBLE_AD_VERSION,
        ].join("/"),
    );
}

/**
 * Записать в статистику клик на рекламу и открытие связанного url.
 */
async function clickAd(
    adId: number,
): Promise<ClickAdApiResponse> {
    return Request.put<ClickAdApiResponse>(
        [
            PATH_ADS,
            PATH_CLICK_AD,
            CLICK_AD_VERSION,
        ].join("/"),
        { adId },
    );
}

export const Ads = {
    checkAccessibleAd,
    clickAd,
};
