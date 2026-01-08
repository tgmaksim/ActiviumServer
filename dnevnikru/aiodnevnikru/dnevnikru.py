from datetime import date
from typing import Optional, Any

from . base import BaseAioDnevnikruApi


__all__ = ['AioDnevnikruApi']


class AioDnevnikruApi(BaseAioDnevnikruApi):
    """TODO"""

    async def get_info(self) -> dict:
        return await self.get("users/me")

    async def get_school(self) -> dict:
        return await self.get("schools/person-schools")

    async def get_person_groups(self, person: int) -> list[dict]:
        return await self.get(f"persons/{person}/edu-groups")

    async def get_person_schedule(self, person: int, group: int, startDate: date, endDate: date) -> dict:
        return await self.get(
            f"persons/{person}/groups/{group}/schedules",
            startDate=str(startDate), endDate=str(endDate)
        )

    async def get_group_lessons(self, group: int, startDate: date, endDate: date) -> list[dict]:
        return await self.get(f"edu-groups/{group}/lessons/{startDate}/{endDate}")

    async def get_group_marks(self, group: int, startDate: date, endDate: date) -> list[dict]:
        return await self.get(f"edu-groups/{group}/marks/{startDate}/{endDate}")

    async def get_work_types(self, gymnasium_id: int) -> list[dict]:
        return await self.get(f"work-types/{gymnasium_id}")

    async def get_group_persons(self, group: int) -> list[dict]:
        return await self.get(f"edu-groups/{group}/students")

    async def get_homeworks(self, homeworks_id: list[int]) -> dict:
        return await self.get("users/me/school/homeworks", homeworkId=homeworks_id)

    async def get_person_recent_marks(
            self,
            person: int,
            group: int,
            from_date: Optional[date] = None,
            subject: Optional[str] = None,
            limit: int = 10
    ) -> dict:
        params: dict[str, Any] = {'limit': limit}
        if from_date:
            params['fromDate'] = from_date.isoformat()
        if subject:
            params['subject'] = subject

        return await self.get(f"persons/{person}/group/{group}/recentmarks", **params)

    async def get_reporting_periods(self, group: int) -> list[dict]:
        return await self.get(f"edu-groups/{group}/reporting-periods")

    async def get_many_marks(self, lessons: list[int]) -> list[dict]:
        return await self.post("lessons/many/marks", data=lessons)

    async def get_marks_by_work(self, work: int) -> list[dict]:
        return await self.get(f"works/{work}/marks")

    async def get_person_marks(self, person: int, subject: int, startDate: date, endDate: date) -> list[dict]:
        return await self.get(f"persons/{person}/subjects/{subject}/marks/{startDate}/{endDate}")

    async def get_group_avg_marks(self, group: int, start: date, finish: date) -> list[dict]:
        return await self.get(f"edu-groups/{group}/avg-marks/{start}/{finish}")

    async def get_person_final_marks(self, person: int, group: int) -> dict:
        return await self.get(f"persons/{person}/edu-groups/{group}/allfinalmarks")
