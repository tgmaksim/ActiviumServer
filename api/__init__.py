from datetime import datetime
from pydnevnikruapi.aiodnevnik import AsyncDiaryAPI


# В оригинальном методе баг
async def get_person_schedule(
    self: AsyncDiaryAPI,
    person_id,
    group_id,
    start_time: str = str(datetime.now()),
    end_time: str = str(datetime.now()),
):
    return await self.get(
        f"persons/{person_id}/groups/{group_id}/schedules",
        params={"startDate": start_time, "endDate": end_time},
    )


AsyncDiaryAPI.get_person_schedule = get_person_schedule
