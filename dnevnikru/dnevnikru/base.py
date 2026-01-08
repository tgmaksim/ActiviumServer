from httpx import Client, Headers, Response
from typing import Any, Union, Sequence, Literal

from dnevnikru.config import dnevnikru_path, login_dnevnikru_path
from dnevnikru.exceptions import InvalidResponseException, DnevnikruApiException


__all__ = ['BaseDnevnikruApi']

type JsonType = Union[list, dict[str, Any]]
type PrimitiveType = Union[str, int, float, bool]
type ParamType = Union[PrimitiveType, Sequence[PrimitiveType]]
type ScopeType = Literal["EducationalInfo", "CommonInfo", "ContactInfo", "FriendsAndRelatives",
                         "SocialInfo", "Files", "Wall", "Messages"]


class BaseDnevnikruApi:
    """
    Базовый класс для совершения API-запросов в дневник.ру

    - Асинхронный режим
    - Библиотека httpx для сетевых запросов
    - Использование PyDantic
    - Проверка возвращаемого результата

    Пример:

    >>> def main():
    ...     dnr = BaseDnevnikruApi(client=..., token=...)
    ...     dnr.get(...)
    ...     dnr.post(...)
    """

    def __init__(self, client: Client, token: str):
        """
        :param client: асинхронный httpx-клиент (рекомендуется сохранять для нескольких запросов)
        :param token: токен для взаимодействия с дневником.ру (получается после авторизации)
        """

        self._client: Client = client
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

        >>> login_url = BaseDnevnikruApi.build_login_url(
        ...     dnevnikru_client_id="abcd",
        ...     scope="EducationalInfo",
        ...     redirect_uri="https://example.com/auth",
        ...     state="session"
        ... )
        """

        if not isinstance(scope, list):
            scope = [scope]

        return str(login_dnevnikru_path.update_query(
            response_type='token',
            client_id=dnevnikru_client_id,
            scope=','.join(scope),
            redirect_uri=redirect_uri,
            state=state
        ))

    def get(
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
        """

        if httpx_kwargs is None:
            httpx_kwargs = {}

        response: Response = self._client.get(
            str(dnevnikru_path.joinpath(method)),
            params=request_params,
            headers=self._headers,
            **httpx_kwargs
        )

        return self._validate_response(response)

    def post(
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
        """

        if httpx_kwargs is None:
            httpx_kwargs = {}

        response: Response = self._client.post(
            str(dnevnikru_path.joinpath(method)),
            params=params,
            json=data,
            headers=self._headers,
            **httpx_kwargs
        )

        return self._validate_response(response)

    def put(
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
        """

        if httpx_kwargs is None:
            httpx_kwargs = {}

        response: Response = self._client.put(
            str(dnevnikru_path.joinpath(method)),
            params=params,
            json=data,
            headers=self._headers,
            **httpx_kwargs
        )

        return self._validate_response(response)

    def delete(
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
        """

        if httpx_kwargs is None:
            httpx_kwargs = {}

        response: Response = self._client.delete(
            str(dnevnikru_path.joinpath(method)),
            params=params,
            headers=self._headers,
            **httpx_kwargs
        )

        return self._validate_response(response)

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
            raise InvalidResponseException(str(error)) from error

        try:
            raise DnevnikruApiException(json['type'], json['description'])
        except (KeyError, TypeError):
            pass

        return json
