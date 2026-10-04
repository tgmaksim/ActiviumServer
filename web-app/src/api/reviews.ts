import type {
    ApiBase,
    ApiResponse,
} from "./base";

import { Request } from "./request";

/**
 * Отзыв.
 */
export interface Review extends ApiBase {
    classId: 0x29;
    reviewId: number;
    name: string;
    stars: number;
    text: string | null;
    likes: number;
    createdAt: string;
    isUpdated: boolean;
}

/**
 * Результат запроса получения своего отзыва.
 */
export interface MyReviewResult extends ApiBase {
    classId: 0x2A;
    review: Review | null;
    onModeration: boolean;
}

/**
 * Ответ на запрос создания отзыва.
 */
export interface CreateReviewApiResponse
    extends ApiResponse<MyReviewResult | null> {
    classId: 0x2B | 0x2;
}

/**
 * Ответ на запрос получения своего отзыва.
 */
export interface MyReviewApiResponse
    extends ApiResponse<MyReviewResult | null> {
    classId: 0x2C | 0x2;
}

/**
 * Ответ на запрос удаления отзыва.
 */
export interface DeleteReviewApiResponse
    extends ApiResponse<null> {
    classId: 0x2D | 0x2;
}

/**
 * Результат запроса получения списка отзывов.
 */
export interface ReviewsResult extends ApiBase {
    classId: 0x2E;
    reviews: Review[];
    nextOffset: number | null;
}

/**
 * Ответ на запрос получения списка отзывов.
 */
export interface ReviewsApiResponse
    extends ApiResponse<ReviewsResult | null> {
    classId: 0x2F | 0x2;
}

/**
 * Результат запроса постановки реакции на отзыв.
 */
export interface LikeReviewResult extends ApiBase {
    classId: 0x30;
    review: Review;
}

/**
 * Ответ на запрос постановки лайка.
 */
export interface LikeReviewApiResponse
    extends ApiResponse<LikeReviewResult | null> {
    classId: 0x31 | 0x2;
}

/**
 * Результат запроса удаления реакции с отзыва.
 */
export interface DeleteReviewLikeResult extends ApiBase {
    classId: 0x32;
    review: Review;
}

/**
 * Ответ на запрос удаления реакции.
 */
export interface DeleteReviewLikeApiResponse
    extends ApiResponse<DeleteReviewLikeResult | null> {
    classId: 0x33 | 0x2;
}

const PATH_PREFIX = "reviews";
const PATH_CREATE_REVIEW = "createReview";
const PATH_GET_MY_REVIEW = "getMyReview";
const PATH_DELETE_REVIEW = "deleteReview";
const PATH_GET_REVIEWS = "getReviews";
const PATH_LIKE_REVIEW = "likeReview";
const PATH_DELETE_REVIEW_LIKE = "deleteReviewLike";

const CREATE_REVIEW_VERSION = 0;
const GET_MY_REVIEW_VERSION = 0;
const DELETE_REVIEW_VERSION = 0;
const GET_REVIEWS_VERSION = 0;
const LIKE_REVIEW_VERSION = 0;
const DELETE_REVIEW_LIKE_VERSION = 0;

/**
 * Отправка или редактирование отзыва о приложение. Отзыв будет опубликован после модерации.
 */
async function createReview(
    stars: number,
    text: string | null,
): Promise<CreateReviewApiResponse> {
    return Request.post<CreateReviewApiResponse>(
        [
            PATH_PREFIX,
            PATH_CREATE_REVIEW,
            CREATE_REVIEW_VERSION,
        ].join("/"),
        { stars },
        text,
    );
}

/**
 * Получение своего отзыва, если такой есть.
 */
async function getMyReview(): Promise<MyReviewApiResponse> {
    return Request.get<MyReviewApiResponse>(
        [
            PATH_PREFIX,
            PATH_GET_MY_REVIEW,
            GET_MY_REVIEW_VERSION,
        ].join("/"),
    );
}

/**
 * Удаление отзыва, если он был ранее опубликован пользователем.
 */
async function deleteReview(): Promise<DeleteReviewApiResponse> {
    return Request.delete<DeleteReviewApiResponse>(
        [
            PATH_PREFIX,
            PATH_DELETE_REVIEW,
            DELETE_REVIEW_VERSION,
        ].join("/"),
    );
}

/**
 * Получение отзывов, написанных другими пользователями, с нужной фильтрацией.
 */
async function getReviews(
    mode: string = "likes",
    offset: number | null = null,
    limit: number = 16,
): Promise<ReviewsApiResponse> {
    const params: Record<string, string | number | boolean> = {
        mode,
        limit,
    };

    if (offset !== null) {
        params.offset = offset;
    }

    return Request.get<ReviewsApiResponse>(
        [
            PATH_PREFIX,
            PATH_GET_REVIEWS,
            GET_REVIEWS_VERSION,
        ].join("/"),
        params,
    );
}

/**
 * Поставить реакцию на отзыв, чтобы поднять его в рейтинге.
 */
async function likeReview(
    reviewId: number,
): Promise<LikeReviewApiResponse> {
    return Request.post<LikeReviewApiResponse>(
        [
            PATH_PREFIX,
            PATH_LIKE_REVIEW,
            LIKE_REVIEW_VERSION,
        ].join("/"),
        { reviewId },
    );
}

/**
 * Удалить ранее поставленную реакцию с отзыва.
 */
async function deleteReviewLike(
    reviewId: number,
): Promise<DeleteReviewLikeApiResponse> {
    return Request.delete<DeleteReviewLikeApiResponse>(
        [
            PATH_PREFIX,
            PATH_DELETE_REVIEW_LIKE,
            DELETE_REVIEW_LIKE_VERSION,
        ].join("/"),
        { reviewId },
    );
}

export const Reviews = {
    createReview,
    getMyReview,
    deleteReview,
    getReviews,
    likeReview,
    deleteReviewLike,
};
