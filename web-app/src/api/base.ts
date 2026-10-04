/**
 * Базовая сущность API.
 */
export interface ApiBase {
    classId: number;
}

/**
 * Ошибка API.
 *
 * @property classId Идентификатор класса.
 * @property type Тип ошибки.
 * @property errorMessage Сообщение об ошибке для показа пользователю.
 */
export interface ApiError extends ApiBase {
    classId: 0x1;
    type: string;
    errorMessage: string | null;
}

/**
 * Базовый ответ API.
 *
 * @property classId Идентификатор класса.
 * @property status Статус выполнения запроса.
 * @property error Объект ошибки.
 * @property answer Ответ в случае успешной обработки.
 */
export interface ApiResponse<TAnswer extends ApiBase | null = ApiBase | null>
    extends ApiBase {
    status: boolean;
    error: ApiError | null;
    answer: TAnswer;
}
