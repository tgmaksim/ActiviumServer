from typing import Optional

from dnevnikru import AioDnevnikruApi
from ...dependencies.httpx import get_httpx_client
from dnevnikru.exceptions import DnevnikruApiException

from ...models.session_model import Session
from ...repositories.db_queue import AsyncDBQueue

from ...repositories.sqlalchemy_repository import SqlAlchemyRepository


__all__ = ['SessionRepository']


class SessionRepository(SqlAlchemyRepository[Session]):
    def __init__(self, queue: AsyncDBQueue):
        super().__init__(queue, Session)

    async def create_session(self, session_id: str):
        await self.create({
            'session_id': session_id
        })

    async def get_session(self, session_id: str) -> Optional[Session]:
        return await self.get_single(Session.session_id == session_id, Session.life == True)

    async def get_sessions(self, parent_id: int) -> list[Session]:
        return await self.get_multi(Session.parent_id == parent_id, Session.life == True)

    async def auth_session(self, session_id: str, dnevnik_token: str, parent_id: int) -> Optional[Session]:
        return await self.update({
            'parent_id': parent_id,
            'dnevnik_token': dnevnik_token
        }, Session.session_id == session_id, Session.life == True)

    async def update_firebase(self, session_id: str, firebase_token: Optional[str]):
        return await self.update({
            'firebase_token': firebase_token
        }, Session.session_id == session_id, Session.life == True)

    async def kill_session(self, session_id: str) -> Optional[Session]:
        return await self.update({'life': False}, Session.session_id == session_id)

    async def check_session_auth(self, session_id: str, dnr: AioDnevnikruApi = None) -> bool:
        session = await self.get_session(session_id)
        if session is None:
            return False

        dnr = dnr or AioDnevnikruApi(get_httpx_client(), session.dnevnik_token)

        try:
            await dnr.get_context()
        except DnevnikruApiException:
            return False
        return True
