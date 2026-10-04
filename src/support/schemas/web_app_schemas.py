from pydantic import Field, BaseModel


__all__ = ['LoginUrl']


class LoginUrl(BaseModel):
    """Ссылка для авторизации"""

    loginUrl: str = Field(
        description="Ссылка для авторизации в Web-приложении"
    )
