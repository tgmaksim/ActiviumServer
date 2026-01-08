from yarl import URL


__all__ = ['dnevnikru_path', 'login_dnevnikru_path']

DNEVNIKRU_API_VERSION = "v2"

dnevnikru_path: URL = URL.build(
    scheme="https",
    host="api.dnevnik.ru",
    path="/" + DNEVNIKRU_API_VERSION
)

login_dnevnikru_path: URL = URL.build(
    scheme="https",
    host="login.dnevnik.ru",
    path="/oauth2"
)
