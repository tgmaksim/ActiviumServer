__all__ = ['SchoolAdminError']


class SchoolAdminError(Exception):
    """Администратор образовательной организации не существует или его сессия не авторизована"""

    def __init__(self, *, user_id: int):
        super().__init__(user_id)
        self.user_id = user_id
