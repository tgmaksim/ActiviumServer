from database import Database
from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI

from . entities import ScheduleHomeworkDocument, ScheduleExtracurricularActivity


async def get_homeworks_files(dnevnik_token: str, homework_id: int) -> list[ScheduleHomeworkDocument]:
    """Получение списка домашних заданий по идентификаторам и возвращение прикрепленных файлов"""

    if not homework_id:
        return []

    async with AsyncDiaryAPI(token=dnevnik_token) as dn:
        # Полная информация о домашних задания
        homeworks = await dn.get_homework_by_id(homework_id)

        result = []
        for homework in homeworks['works']:
            for file_id in homework['files']:
                for file in homeworks['files']:
                    if file['id'] == file_id:
                        result.append(ScheduleHomeworkDocument(
                            fileName=file['name'] + '.' + file['type'].lower(),
                            downloadUrl=file['downloadUrl']
                        ))

        return result


async def get_extracurricular_activities(group_id: int, weekday: int, day: str) -> list[ScheduleExtracurricularActivity]:
    """Получение внеурочек класса в данный день с предметом и кабинетом"""

    sql = "SELECT subject, place FROM extracurricular_activities WHERE group_id = $1 AND weekday = $2 AND day = $3"
    extracurricular_activities = await Database.fetch_all(sql, group_id, weekday, day)

    result = []
    for extracurricular_activity in extracurricular_activities:
        result.append(ScheduleExtracurricularActivity(
            subject=extracurricular_activity['subject'],
            place=str(extracurricular_activity['place']),
        ))

    return result
