from typing import Any, Union, Sequence, Literal
from httpx import AsyncClient, Headers, Response, TimeoutException

from dnevnikru.config import dnevnikru_path, login_dnevnikru_path
from dnevnikru.exceptions import InvalidResponseException, DnevnikruApiException, RequestTimeoutException


__all__ = ['BaseAioDnevnikruApi']

type JsonType = Union[list, dict[str, Any]]
type PrimitiveType = Union[str, int, float, bool]
type ParamType = Union[PrimitiveType, Sequence[PrimitiveType]]
type ScopeType = Literal["EducationalInfo", "CommonInfo", "ContactInfo", "FriendsAndRelatives",
                         "SocialInfo", "Files", "Wall", "Messages"]


class BaseAioDnevnikruApi:
    """
    Базовый класс для совершения API-запросов в дневник.ру

    - Асинхронный режим
    - Библиотека httpx для сетевых запросов
    - Использование PyDantic
    - Проверка возвращаемого результата

    Пример:

    >>> async def main():
    ...     dnr = BaseAioDnevnikruApi(client=..., token=...)
    ...     await dnr.get(...)
    ...     await dnr.post(...)
    """

    def __init__(self, client: AsyncClient, token: str):
        """
        Создание экземпляра клиента для взаимодействия с API Дневника.ру

        :param client: асинхронный httpx-клиент (рекомендуется сохранять для нескольких запросов)
        :param token: токен для взаимодействия с Дневником.ру (получается после авторизации)
        """

        self._client: AsyncClient = client
        self._token: str = token
        self._headers: Headers = Headers({'Access-Token': token})

    @staticmethod
    def build_login_url(
            dnevnikru_client_id: str,
            scope: Union[ScopeType, list[ScopeType]],
            redirect_uri: str,
            state: str
    ) -> str:
        """
        Получение ссылки для создания API-токена, который необходим для совершения запросов

        :param dnevnikru_client_id: ключ приложения, полученный от дневника.ру
        :param scope: права(-о) доступа, требуемые от пользователя
        :param redirect_uri: URI для перенаправления после (не)успешной авторизации
        :param state: специальный параметр, который передается в redirect_uri для идентификации
        :return: готовая ссылка для создания API-токена дневника.ру

        Примеры:

        >>> login_url = BaseAioDnevnikruApi.build_login_url(
        ...     dnevnikru_client_id="abcd",
        ...     scope="EducationalInfo",
        ...     redirect_uri="https://example.com/auth",
        ...     state="session"
        ... )
        """

        if not isinstance(scope, list):
            scope = [scope]

        return str(login_dnevnikru_path.update_query(
            response_type='token',  # Тип возвращаемого ответа - токен будет в redirect_uri#hash
            client_id=dnevnikru_client_id,
            scope=','.join(scope),
            redirect_uri=redirect_uri,
            state=state
        ))

    async def _request(
            self,
            method: str,
            path: str,
            *,
            data: Any = None,
            httpx_kwargs: dict[str, Any] = None,
            **request_params: ParamType
    ) -> JsonType:
        """
        API-запрос и валидация ответа

        :param method http-метод запроса
        :param path: название (путь) метода
        :param httpx_kwargs: дополнительные параметры для httpx
        :param request_params: параметры API-запроса в пути (?query)
        :return: результат в виде JSON
        :except InvalidResponseError: Некорректный ответ от дневника.ру, привлекший к ошибке
        :except DnevnikruApiError: Ошибка в API-запросе от дневника.ру
        :except RequestTimeoutException: Превышен лимит ожидания ответа от дневника.ру
        """

        if httpx_kwargs is None:
            httpx_kwargs = {}

        try:
            response: Response = await self._client.request(
                method,
                str(dnevnikru_path.joinpath(path)),
                params=request_params,
                json=data,
                headers=self._headers,
                **httpx_kwargs
            )
        except TimeoutException as e:
            raise RequestTimeoutException(e)

        return self._validate_response(response)

    async def get(
            self,
            method: str,
            *,
            httpx_kwargs: dict[str, Any] = None,
            **request_params: ParamType
    ) -> JsonType:
        """
        API-запрос с помощью метода GET и валидация ответа

        :param method: название (путь) метода
        :param httpx_kwargs: дополнительные параметры для httpx
        :param request_params: параметры API-запроса в пути (?query)
        :return: результат в виде JSON
        :except InvalidResponseError: Некорректный ответ от дневника.ру, привлекший к ошибке
        :except DnevnikruApiError: Ошибка в API-запросе от дневника.ру
        :except RequestTimeoutException: Превышен лимит ожидания ответа от дневника.ру
        """

        return await self._request("GET", method, httpx_kwargs=httpx_kwargs, **request_params)

    async def post(
            self,
            method: str,
            *,
            params: dict[str, Any] = None,
            data: Any = None,
            httpx_kwargs: dict[str, Any] = None
    ) -> JsonType:
        """
        API-запрос с помощью метода POST и валидация ответа

        :param method: название (путь) метода
        :param params: параметры API-запроса в пути (?query)
        :param data: параметры API-запроса в теле запроса в виде JSON
        :param httpx_kwargs: дополнительные параметры для httpx
        :return: результат в виде JSON
        :except InvalidResponseError: Некорректный ответ от дневника.ру, привлекший к ошибке
        :except DnevnikruApiError: Ошибка в API-запросе от дневника.ру
        :except RequestTimeoutException: Превышен лимит ожидания ответа от дневника.ру
        """

        if params is None:
            params = {}

        return await self._request("POST", method, data=data, httpx_kwargs=httpx_kwargs, **params)

    async def put(
            self,
            method: str,
            *,
            params: dict[str, Any] = None,
            data: Any = None,
            httpx_kwargs: dict[str, Any] = None
    ) -> JsonType:
        """
        API-запрос с помощью метода PUT и валидация ответа

        :param method: название (путь) метода
        :param params: параметры API-запроса в пути (?query)
        :param data: параметры API-запроса в теле запроса в виде JSON
        :param httpx_kwargs: дополнительные параметры для httpx
        :return: результат в виде JSON
        :except InvalidResponseError: Некорректный ответ от дневника.ру, привлекший к ошибке
        :except DnevnikruApiError: Ошибка в API-запросе от дневника.ру
        :except RequestTimeoutException: Превышен лимит ожидания ответа от дневника.ру
        """

        if params is None:
            params = {}

        return await self._request("PUT", method, data=data, httpx_kwargs=httpx_kwargs, **params)

    async def delete(
            self,
            method: str,
            *,
            params: dict[str, Any] = None,
            httpx_kwargs: dict[str, Any] = None
    ) -> JsonType:
        """
        API-запрос с помощью метода DELETE и валидация ответа

        :param method: название (путь) метода
        :param params: параметры API-запроса в пути (?query)
        :param httpx_kwargs: дополнительные параметры для httpx
        :return: результат в виде JSON
        :except InvalidResponseError: Некорректный ответ от дневника.ру, привлекший к ошибке
        :except DnevnikruApiError: Ошибка в API-запросе от дневника.ру
        :except RequestTimeoutException: Превышен лимит ожидания ответа от дневника.ру
        """

        if params is None:
            params = {}

        return await self._request("DELETE", method, httpx_kwargs=httpx_kwargs, **params)

    @staticmethod
    def _validate_response(response: Response) -> JsonType:
        """
        Валидация ответа к нужному типу или возвращение ошибки

        :param response: ответ с данными
        :return: результат в виде JSON
        :except InvalidResponseError: Некорректный ответ от дневника.ру, привлекший к ошибке
        :except DnevnikruApiError: Ошибка в API-запросе от дневника.ру
        """

        content_type: str = response.headers.get('content-type').split(';')[0]
        if content_type != 'application/json':
            raise InvalidResponseException(f"Content type is {content_type}, not application/json")

        try:
            json = response.json()
        except Exception as error:
            raise InvalidResponseException(error) from error

        try:
            raise DnevnikruApiException(json['type'], json['description'])
        except (KeyError, TypeError):
            pass

        return json
