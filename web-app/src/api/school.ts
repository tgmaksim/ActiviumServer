import type {
    ApiBase,
    ApiResponse,
} from "./base";

import { Request } from "./request";

/**
 * Школьный пост.
 *
 * @property classId Идентификатор класса.
 * @property postId Идентификатор поста.
 * @property title Заголовок поста.
 * @property description Короткое описание поста, если есть.
 * @property imageUrl Ссылка на главную картинку поста.
 * @property author Имя автора поста.
 * @property authorVerified Автор является сотрудником Активиум.
 * @property scheduleDate Дата мероприятия в расписании.
 * @property humanScheduleDate Дата мероприятия в расписании в нужном формате строки для показа пользователю.
 * @property isUpdated Пост был отредактирован после написания.
 * @property countViewings Количество полных просмотров поста.
 * @property countLikes Количество реакций.
 * @property hasMyLike Поставлена реакция на пост.
 * @property isSaw Пост был увиден.
 * @property postUrl Ссылка на открытие поста.
 * @property createdAt Время написания поста.
 * @property humanCreatedAt Время написания поста в нужном формате строки для показа пользователю.
 */
export interface SchoolPost extends ApiBase {
    classId: 0x4E;
    postId: number;
    title: string;
    description: string | null;
    imageUrl: string | null;
    author: string;
    authorVerified: boolean;
    scheduleDate: string | null;
    humanScheduleDate: string | null;
    isUpdated: boolean;
    countViewings: number;
    countLikes: number;
    hasMyLike: boolean;
    isSaw: boolean;
    postUrl: string;
    createdAt: string;
    humanCreatedAt: string;
}

/**
 * Результат запроса получения последних постов.
 *
 * @property posts Список постов.
 * @property nextOffset Смещение для получения следующих постов.
 */
export interface SchoolPostsResult extends ApiBase {
    classId: 0x4F;
    posts: SchoolPost[];
    nextOffset: number | null;
}

/**
 * Ответ на запрос получения последних постов.
 */
export interface SchoolPostsApiResponse
    extends ApiResponse<SchoolPostsResult | null> {
    classId: 0x50 | 0x2;
}

/**
 * Результат запроса получения неувиденных постов.
 *
 * @property countPosts Количество неувиденных постов.
 */
export interface SchoolPostsWithoutVisionResult extends ApiBase {
    classId: 0x51;
    countPosts: number;
}

/**
 * Ответ на запрос получения неувиденных постов.
 */
export interface SchoolPostsWithoutVisionApiResponse
    extends ApiResponse<SchoolPostsWithoutVisionResult | null> {
    classId: 0x52 | 0x2;
}

/**
 * Результат запроса пометки поста.
 *
 * @property post Обновленный пост.
 * @property countPostsWithoutVision Количество неувиденных постов.
 */
export interface MarkSchoolPostResult extends ApiBase {
    classId: 0x53;
    post: SchoolPost;
    countPostsWithoutVision: number;
}

/**
 * Ответ на запрос пометки поста как увиденного.
 */
export interface SeeSchoolPostApiResponse
    extends ApiResponse<MarkSchoolPostResult | null> {
    classId: 0x54 | 0x2;
}

/**
 * Ответ на запрос пометки поста как нажатого.
 */
export interface ClickSchoolPostApiResponse
    extends ApiResponse<MarkSchoolPostResult | null> {
    classId: 0x55 | 0x2;
}

/**
 * Ответ на запрос просмотра поста.
 */
export interface ViewSchoolPostApiResponse
    extends ApiResponse<MarkSchoolPostResult | null> {
    classId: 0x56 | 0x2;
}

/**
 * Ответ на запрос постановки реакции.
 */
export interface LikeSchoolPostApiResponse
    extends ApiResponse<MarkSchoolPostResult | null> {
    classId: 0x57 | 0x2;
}

/**
 * Ответ на запрос удаления реакции.
 */
export interface UnlikeSchoolPostApiResponse
    extends ApiResponse<MarkSchoolPostResult | null> {
    classId: 0x58 | 0x2;
}

const PATH_PREFIX = "school";

const PATH_GET_POSTS = "getPosts";
const PATH_CHECK_NEW_POSTS = "checkNewPosts";
const PATH_SEE_POST = "seePost";
const PATH_CLICK_POST = "clickPost";
const PATH_VIEW_POST = "viewPost";
const PATH_LIKE_POST = "likePost";
const PATH_UNLIKE_POST = "unlikePost";

const GET_POSTS_VERSION = 0;
const CHECK_NEW_POSTS_VERSION = 0;
const SEE_POST_VERSION = 0;
const CLICK_POST_VERSION = 0;
const VIEW_POST_VERSION = 0;
const LIKE_POST_VERSION = 0;
const UNLIKE_POST_VERSION = 0;

/**
 * Получение последних постов, отсортированных по дате публикации.
 *
 * @param offset Смещение постов.
 */
async function getPosts(
    offset: number,
): Promise<SchoolPostsApiResponse> {
    return Request.get<SchoolPostsApiResponse>(
        [
            PATH_PREFIX,
            PATH_GET_POSTS,
            GET_POSTS_VERSION,
        ].join("/"),
        {
            offset,
        },
    );
}

/**
 * Получение количества неувиденных постов, но только тех,
 * которые были опубликованы не ранее, чем 14 дней назад.
 */
async function checkNewPosts(): Promise<SchoolPostsWithoutVisionApiResponse> {
    return Request.get<SchoolPostsWithoutVisionApiResponse>(
        [
            PATH_PREFIX,
            PATH_CHECK_NEW_POSTS,
            CHECK_NEW_POSTS_VERSION,
        ].join("/"),
    );
}

/**
 * Пометить пост увиденным. После этого метод /checkNewPosts
 * не будет считать его.
 *
 * @param postId Идентификатор поста.
 */
async function seePost(
    postId: number,
): Promise<SeeSchoolPostApiResponse> {
    return Request.put<SeeSchoolPostApiResponse>(
        [
            PATH_PREFIX,
            PATH_SEE_POST,
            SEE_POST_VERSION,
        ].join("/"),
        {
            postId,
        },
    );
}

/**
 * Пометить пост нажатым.
 *
 * @param postId Идентификатор поста.
 */
async function clickPost(
    postId: number,
): Promise<ClickSchoolPostApiResponse> {
    return Request.put<ClickSchoolPostApiResponse>(
        [
            PATH_PREFIX,
            PATH_CLICK_POST,
            CLICK_POST_VERSION,
        ].join("/"),
        {
            postId,
        },
    );
}

/**
 * Пометить пост просмотренным.
 *
 * @param postId Идентификатор поста.
 */
async function viewPost(
    postId: number,
): Promise<ViewSchoolPostApiResponse> {
    return Request.put<ViewSchoolPostApiResponse>(
        [
            PATH_PREFIX,
            PATH_VIEW_POST,
            VIEW_POST_VERSION,
        ].join("/"),
        {
            postId,
        },
    );
}

/**
 * Поставить реакцию на пост.
 *
 * @param postId Идентификатор поста.
 */
async function likePost(
    postId: number,
): Promise<LikeSchoolPostApiResponse> {
    return Request.put<LikeSchoolPostApiResponse>(
        [
            PATH_PREFIX,
            PATH_LIKE_POST,
            LIKE_POST_VERSION,
        ].join("/"),
        {
            postId,
        },
    );
}

/**
 * Убрать реакцию с поста.
 *
 * @param postId Идентификатор поста.
 */
async function unlikePost(
    postId: number,
): Promise<UnlikeSchoolPostApiResponse> {
    return Request.put<UnlikeSchoolPostApiResponse>(
        [
            PATH_PREFIX,
            PATH_UNLIKE_POST,
            UNLIKE_POST_VERSION,
        ].join("/"),
        {
            postId,
        },
    );
}

/**
 * API-запросы группы school.
 */
export const School = {
    getPosts,
    checkNewPosts,
    seePost,
    clickPost,
    viewPost,
    likePost,
    unlikePost,
};