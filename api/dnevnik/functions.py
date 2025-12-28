from database import Database

from pydnevnikruapi.aiodnevnik.dnevnik import AsyncDiaryAPI

from . entities import ScheduleHomeworkDocument, ScheduleExtracurricularActivity


async def get_homeworks_files(dnevnik_token: str, homework_id: int) -> list[ScheduleHomeworkDocument]:
    """
    Получение списка домашних заданий по идентификаторам и возвращение прикрепленных файлов

    :param dnevnik_token: токен для взаимодействия с аккаунтом дневника.ру
    :param homework_id: идентификатор домашнего задания
    :return: список прикрепленных файлов к домашнему заданию
    """

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


async def get_extracurricular_activities(gymnasium_id: int, group_id: int, weekday: int, day_hash: str) -> list[ScheduleExtracurricularActivity]:
    """
    Получение внеурочных занятий класса в данный день с предметом и кабинетом

    :param gymnasium_id: идентификатор школы ученика(цы) в дневнике.ру
    :param group_id: идентификатор класса ученика(цы) в дневнике.ру
    :param weekday: индекс дня недели
    :param day_hash: md5-хеш отсортированного списка идентификаторов предметов в данный день
    :return: список внеурочных занятий
    """

    sql = "SELECT subject, place FROM extracurricular_activities WHERE gymnasium_id = $1 AND group_id = $2 AND weekday = $3 AND day = $4"
    extracurricular_activities = await Database.fetch_all(sql, gymnasium_id, group_id, weekday, day_hash)

    result = []
    for extracurricular_activity in extracurricular_activities:
        result.append(ScheduleExtracurricularActivity(
            subject=extracurricular_activity['subject'],
            place=str(extracurricular_activity['place']),
        ))

    return result
