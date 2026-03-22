from datetime import date, datetime
from typing import Optional, Any, Union

from . base import BaseDnevnikruApi


__all__ = ['DnevnikruApi']


class DnevnikruApi(BaseDnevnikruApi):
    def get_info(self) -> dict:
        """Общая информация о текущем пользователе"""

        return self.get("users/me")

    def get_context(self) -> dict:
        """Полная контекстная информация текущего пользователя и его детей"""

        return self.get("users/me/context")

    def get_schools(self, excludeOrganizations: bool = True) -> list[dict]:
        """Школы и другие организации, в которых состоит пользователь"""

        return self.get("schools/person-schools", excludeOrganizations=excludeOrganizations)

    def get_person_groups(self, person: int) -> list[dict]:
        """Классы и другие учебные группы (например, подгруппы класса) персоны"""

        return self.get(f"persons/{person}/edu-groups")

    def get_person_schedule(self, person: int, group: int, startDate: Union[str, datetime, date], endDate: Union[str, datetime, date]) -> dict:
        """Расписание персоны в учебной группе"""

        return self.get(
            f"persons/{person}/groups/{group}/schedules",
            startDate=str(startDate), endDate=str(endDate)
        )

    def get_group_lessons(self, group: int, startDate: date, endDate: date) -> list[dict]:
        """Уроки всей учебной группы, в том числе разных подгрупп"""

        return self.get(f"edu-groups/{group}/lessons/{startDate}/{endDate}")

    def get_group_marks(self, group: int, startDate: date, endDate: date) -> list[dict]:
        """Оценки учебной группы"""

        return self.get(f"edu-groups/{group}/marks/{startDate}/{endDate}")

    def get_work_types(self, school_id: int) -> list[dict]:
        """Существующие типы работ в образовательной организации"""

        return self.get(f"work-types/{school_id}")

    def get_group_persons(self, group: int) -> list[dict]:
        """Персоны в учебной группе"""

        return self.get(f"edu-groups/{group}/students")

    def get_homeworks(self, homeworks_id: list[int]) -> dict:
        """Домашние задания по идентификаторам"""

        return self.get("users/me/school/homeworks", homeworkId=homeworks_id)

    def get_person_recent_marks(
            self,
            person: int,
            group: int,
            from_date: Optional[Union[datetime, date]] = None,
            subject: Optional[str] = None,
            limit: int = 10
    ) -> dict:
        """Последние по дате выставления оценки персоны в учебной группе"""

        params: dict[str, Any] = {'limit': limit}
        if from_date:
            params['fromDate'] = str(from_date)
        if subject:
            params['subject'] = subject

        return self.get(f"persons/{person}/group/{group}/recentmarks", **params)

    def get_reporting_periods(self, group: int) -> list[dict]:
        """Отчетные периоды в учебной группе"""

        return self.get(f"edu-groups/{group}/reporting-periods")

    def get_many_marks(self, lessons: list[int]) -> list[dict]:
        """Все оценки за урок в учебной группе"""

        return self.post("lessons/many/marks", data=lessons)

    def get_marks_by_work(self, work: int) -> list[dict]:
        """Все оценки за работу на уроке в учебной группе"""

        return self.get(f"works/{work}/marks")

    def get_person_subject_marks(self, person: int, subject: int, startDate: date, endDate: date) -> list[dict]:
        """Оценки персоны по предмету в текущем отчетном периоде"""

        return self.get(f"persons/{person}/subjects/{subject}/marks/{startDate}/{endDate}")

    def get_group_avg_marks(self, group: int, start: date, finish: date) -> list[dict]:
        """Средние баллы по предметам в учебной группе"""

        return self.get(f"edu-groups/{group}/avg-marks/{start}/{finish}")

    def get_person_final_marks(self, person: int, group: int) -> dict:
        """Оценки персоны по предметам за каждый отчетный период в текущем учебном году и за год"""

        return self.get(f"persons/{person}/edu-groups/{group}/allfinalmarks")

    def get_children(self, person_id: int) -> list[dict]:
        """Дети персоны"""

        return self.get(f"person/{person_id}/children")

    def get_lesson(self, lesson_id: int) -> dict:
        """Урок по идентификатору"""

        return self.get(f"lessons/{lesson_id}")

    def get_group_avg_marks_by_date(self, group: int, period: int, _date: date) -> list[dict]:
        """Средние баллы по предметам в учебной группе на момент определенной даты"""

        return self.get(f"edu-groups/{group}/reporting-periods/{period}/avg-marks/{_date}")

    def get_user_info(self, user: int) -> dict:
        """Общая информация о пользователе"""

        return self.get(f"users/{user}")

    def get_person_marks(self, person: int, group: int, startDate: date, endDate: date) -> list[dict]:
        """Оценки персоны по предметам в учебной группе"""

        return self.get(f"persons/{person}/edu-groups/{group}/marks/{startDate}/{endDate}")

    def get_many_lessons(self, lessons: list[int]) -> list[dict]:
        """Уроки по идентификаторам"""

        return self.post("lessons/many", data=lessons)

    def get_marks_by_lesson(self, lesson: int) -> list[dict]:
        """Все оценки за урок в учебной группе"""

        return self.get(f"lessons/{lesson}/marks")

    def get_person(self, person: int) -> dict:
        """Персона по идентификатору"""

        return self.get(f"persons/{person}")

    def get_person_marks_by_lesson(self, person: int, lesson: int) -> list[dict]:
        """Оценки персоны за урок в учебной группе"""

        return self.get(f"persons/{person}/lessons/{lesson}/marks")
