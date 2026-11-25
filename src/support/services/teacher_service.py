import secrets

from pathlib import Path
from asyncio import gather
from datetime import datetime, UTC
from typing import Optional, Callable, Union

from yarl import URL
from httpx import AsyncClient
from starlette.status import HTTP_404_NOT_FOUND

from dnevnikru import AioDnevnikruApi, DnevnikruApiException

from ...schemas.error_schema import ApiError
from ...config.project_config import settings
from ...repositories.log_uow import LogUnitOfWork
from ...services.html_response import HtmlResponse
from ...repositories.statistic_repository import StatName

from ..schemas.teacher_schemas import SubjectsList, Subject

from ...services.log_service import LogService
from ...services.base_service import BaseService
from ..repositories.app_uow import AppUnitOfWork
from ...utils.cache import CacheService

from ...utils.exception import format_exception

from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.lib.enums import TA_CENTER
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    PageTemplate,
    Table,
    TableStyle,
    Paragraph,
    Spacer,
    KeepTogether,
)


__all__ = ['TeacherService']


class TeacherService(BaseService[AppUnitOfWork]):
    """Сервис для работы помощника учителя"""

    def __init__(self, uow_factory: Callable[[], AppUnitOfWork], log_uow_factory: Callable[[], LogUnitOfWork], httpx_client: AsyncClient):
        super().__init__(uow_factory)
        self.httpx_client = httpx_client
        self.log_service = LogService(log_uow_factory)

    async def root(self, session_id: Optional[str]) -> HtmlResponse:
        authorized = bool(session_id)
        parent_id: Optional[int] = None
        login_url: Optional[str] = None
        classes: Optional[list[dict]] = None

        if authorized:
            async with self.uow_factory() as uow:
                session = await uow.teacher_session_repository.get_session(session_id)

            if session is None:
                authorized = False
            else:
                dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

                try:
                    context = await dnr.get_context()

                    schools = context['schools']
                    schools_id = [school['id'] for school in schools]
                    school_names = {school['id']: school['name'] for school in schools}

                    groups: tuple[Union[list[dict], BaseException]] = await gather(*(dnr.get_school_groups(school_id) for school_id in schools_id), return_exceptions=True)
                    zip_groups: list[tuple[int, Union[list[dict], BaseException]]] = list(zip(schools_id, groups))
                    groups_by_school: dict[int, list[dict]] = {
                        school_id: groups_or_exception
                        for school_id, groups_or_exception in zip_groups
                        if isinstance(groups_or_exception, list)
                    }
                except DnevnikruApiException as e:
                    authorized = False
                    await self.log_service.log(
                        ip='127.0.0.1',
                        path='teacher_root',
                        status=False,
                        value=format_exception(e)
                    )
                else:
                    parent_id = context['personId']
                    classes = [
                        {
                            'name': group['name'] if len(groups_by_school) == 1 else f"{group['name']} {school_names[school_id]}",
                            'groupId': group['id']
                        }
                        for school_id, school_groups in groups_by_school.items() for group in school_groups
                    ]

        if not authorized:  # Если сессии нет или сессия не работает
            login_url = AioDnevnikruApi.build_login_url(
                dnevnikru_client_id=settings.DNEVNIK_CLIENT_ID,
                scope=["EducationalInfo", "CommonInfo", "FriendsAndRelatives"],
                redirect_uri=str(URL(settings.URL).joinpath("teacher/auth")),
                state=""  # Сессия генерируется при авторизации
            )

        csrf_token = secrets.token_urlsafe(16)

        async with self.uow_factory() as uow:
            await uow.statistic_repository.add_statistic(parent_id, StatName.teacher)

        return HtmlResponse(
            name='teacher.html',
            context={
                'project_name': settings.PROJECT_NAME_RU,
                'csrf_token': csrf_token,
                'authorized': authorized,
                'login_url': login_url or "",
                'classes': classes or []
            },
            cookies=[
                {
                    'key': 'csrf_token',
                    'value': csrf_token,
                    'max_age': 5 * 60,  # 5 минут
                    'httponly': False,
                    'samesite': 'lax'
                }
            ]
        )

    @classmethod
    async def firstAuth(cls) -> HtmlResponse:
        return HtmlResponse(
            name='auth_session.html',
            context={
                'project_name': settings.PROJECT_NAME_RU
            }
        )

    async def secondAuth(self, dnevnik_token: str) -> HtmlResponse:
        dnr = AioDnevnikruApi(self.httpx_client, dnevnik_token)

        context = await dnr.get_context()
        teacher_id: int = context['personId']
        roles = list(map(str, context['roles']))

        if 'EduStaff' not in roles and 'EduSchoolAdministrator' not in roles:
            return HtmlResponse(
                name='error.html',
                status_code=400,
                context={
                    'title': "Ошибка авторизации",
                    'description': "Вы не являетесь учителем или администратором образовательной организации"
                }
            )

        async with self.uow_factory() as uow:
            teacher = await uow.teacher_repository.get_teacher(teacher_id)
            if teacher is None:
                await uow.teacher_repository.create_teacher(teacher_id)
                await uow.statistic_repository.add_statistic(teacher_id, StatName.teacherRegistration)

            for i in range(10):
                teacher_session = await uow.teacher_session_repository.create_teacher_session(
                    secrets.token_hex(16), teacher_id, dnevnik_token)

                if teacher_session is not None:
                    break

            if teacher_session is not None:
                await uow.statistic_repository.add_statistic(teacher_id, StatName.teacherAuthorization)

        if teacher_session is None:
            raise RuntimeError('teacher session creation failed')

        return HtmlResponse(
            name='teacher.html',
            context={
                'project_name': settings.PROJECT_NAME_RU
            },
            cookies=[
                {
                    'key': 'teacher_session_id',
                    'value': teacher_session.session_id,
                    'max_age': 90 * 24 * 60 * 60,
                    'httponly': True,
                    'secure': True,
                    'samesite': 'lax'
                }
            ]
        )

    async def list_subjects(self, session_id: str, group_id: int) -> Optional[SubjectsList]:
        async with self.uow_factory() as uow:
            session = await uow.teacher_session_repository.get_session(session_id)

        if session is None:
            return None

        dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

        try:
            subjects = await dnr.get_subjects(group_id)
        except DnevnikruApiException as e:
            if not await uow.teacher_session_repository.check_session_auth(session_id, dnr):
                return None
            if e.type == 'parameterInvalid':
                raise ApiError(
                    type="GroupNotFoundError",
                    errorMessage="Учебная группа не найдена"
                ).exception(HTTP_404_NOT_FOUND)
            raise

        return [Subject(
            id=str(subject['id']),
            name=subject['name']
        ) for subject in subjects]

    async def create_report(
            self, session_id: str, group_id: int,
            without_marks: bool, average: bool, period_marks: bool, signature_lines: bool,
            rating: bool, list_subjects: Optional[list[int]]
    ) -> Union[tuple[Path, str], HtmlResponse]:
        async with self.uow_factory() as uow:
            session = await uow.teacher_session_repository.get_session(session_id)

        csrf_token = secrets.token_urlsafe(16)
        root_result = HtmlResponse(
            name='teacher.html',
            context={
                'project_name': settings.PROJECT_NAME_RU,
                'csrf_token': csrf_token,
                'authorized': False
            },
            cookies=[
                {
                    'key': 'csrf_token',
                    'value': csrf_token,
                    'max_age': 5 * 60,
                    'httponly': False,
                    'samesite': 'lax'
                }
            ],
            delete_cookies=[
                {
                    'key': 'teacher_session_id'
                }
            ]
        )

        if session is None:
            return root_result

        dnr = AioDnevnikruApi(self.httpx_client, session.dnevnik_token)

        try:
            group, periods, _persons, _subjects, final_marks = await gather(
                dnr.get_group(group_id),
                dnr.get_reporting_periods(group_id),
                dnr.get_group_persons(group_id),
                dnr.get_subjects(group_id),
                dnr.get_group_final_marks(group_id)
            )
        except DnevnikruApiException:
            if not await uow.teacher_session_repository.check_session_auth(session_id, dnr):
                return root_result
            raise

        persons: dict[int, str] = {person['id']: person['shortName'] for person in _persons}
        subjects: dict[int, str] = {
            subject['id']: subject['name'] for subject in _subjects
            if list_subjects is None or subject['id'] in list_subjects
        }

        periods = sorted(periods, key=lambda p: datetime.fromisoformat(p['start']))
        active_period = CacheService.get_active_period(periods, datetime.now(UTC).date())

        final_marks_by_work_id = {
            final_mark['final-mark']['work']: final_mark['final-mark']
            for person in final_marks for final_mark in person['per-subject-final-marks']
        }

        marks, avg_marks, final_works = await gather(
            dnr.get_group_marks(group_id, active_period['start'], active_period['finish']),
            dnr.get_group_avg_marks(group_id, active_period['start'], active_period['finish']),
            dnr.get_works(list(final_marks_by_work_id))
        )

        # Первый ключ по ученику, второй по названию предмета.
        # Данные в виде кортежа: первый элемент - список оценок,
        # второй элемент - список из одного элемента - среднего балла по предмету (оценка или пустая строка),
        # третий элемент - список из одного элемента - итоговой оценки за период по предмету (оценка или пустая строка)
        marks_by_person_id_subject: dict[int, dict[str, tuple[list[str], list[str], list[str]]]] = {}

        works_ids = {mark['work'] for mark in marks}
        _works = await dnr.get_works(list(works_ids))
        works = {work['id']: work for work in _works}

        for mark in marks:
            if marks_by_person_id_subject.get(mark['person']) is None:
                marks_by_person_id_subject[mark['person']] = {subject: ([], [''], ['']) for subject in subjects.values()}

            subject = subjects.get(works[mark['work']]['subjectId'])
            if subject is None:
                continue

            marks_by_person_id_subject[mark['person']][subject][0].append(mark['textValue'])

        class_rating: list[tuple[float, str]] = []

        for person in avg_marks:
            if marks_by_person_id_subject.get(person['person']) is None:
                marks_by_person_id_subject[person['person']] = {subject: ([], [''], ['']) for subject in subjects.values()}

            for avg_mark in person['per-subject-averages']:
                subject = subjects.get(avg_mark['subject'])
                if subject is None:
                    continue

                marks_by_person_id_subject[person['person']][subject][1][0] = avg_mark['avg-mark-value']

            if (count := len(person['per-subject-averages'])) == 0:
                continue

            sum_marks = sum(float(mark['avg-mark-value'].replace(',', '.')) for mark in person['per-subject-averages'])
            avg_mark = round(sum_marks / count, 2)

            class_rating.append((avg_mark, persons.get(person['person'], "Неизвестный ученик")))

        for work in final_works:
            if work['periodNumber'] != active_period['number']:
                continue

            final_mark = final_marks_by_work_id[work['id']]
            subject = subjects.get(work['subjectId'])
            if subject is None:
                continue

            if marks_by_person_id_subject.get(final_mark['person']) is None:
                marks_by_person_id_subject[final_mark['person']] = {subject: ([], [''], ['']) for subject in subjects.values()}

            marks_by_person_id_subject[final_mark['person']][subject][2][0] = final_mark['textValue']

        class_rating.sort(reverse=True)

        class_rating_with_positions: list[tuple[int, str, float]] = []
        last_position = 1
        last_avg = None
        for i, (avg_mark, person_name) in enumerate(class_rating):
            if avg_mark != last_avg:
                last_position = i + 1
            class_rating_with_positions.append((last_position, person_name, avg_mark))
            last_avg = avg_mark

        marks_by_person_subject: list[tuple[str, dict[str, tuple[list[str], list[str], list[str]]]]] = [
            (
                person_name,
                marks_by_person_id_subject.get(
                    person_id,
                    {subject: ([], [''], ['']) for subject in subjects.values()}
                ),
            )
            for person_id, person_name in persons.items()
        ]

        report_creator = ReportCreator(
            session.teacher_id, marks_by_person_subject,
            class_rating_with_positions if rating else None, without_marks, average, period_marks, signature_lines
        )
        pdf = report_creator.create_pdf()

        async with self.uow_factory() as uow:
            await uow.statistic_repository.add_statistic(session.teacher_id, StatName.teacherCreateReport)

        return pdf, group['fullName']


class ReportCreator:
    class WatermarkedTable(Table):
        def draw(self):
            super().draw()

            self.canv.saveState()
            self.canv.setFont("DejaVuSans", 9)
            self.canv.setFillColor(colors.HexColor("#C8C8C8"))
            self.canv.drawRightString(
                self._width - 3,
                3,
                settings.PROJECT_NAME_RU,
            )
            self.canv.restoreState()

    def __init__(
        self,
        teacher_id: int,
        data: list[tuple[str, dict[str, tuple[list[str], list[str], list[str]]]]],
        rating: Optional[list[tuple[int, str, float]]],
        without_marks: bool,
        average: bool,
        period_marks: bool,
        signature_lines: bool
    ):
        self.teacher_id = teacher_id
        self.data = data
        self.rating = rating
        self.without_marks = without_marks
        self.average = average
        self.period_marks = period_marks
        self.signature_lines = signature_lines

        # Параметры страницы
        self.page_width, self.page_height = A4
        self.margin_x = 10 * mm
        self.margin_y = 10 * mm
        self.column_gap = 4 * mm

        self.available_width = self.page_width - 2 * self.margin_x
        self.table_width = (self.available_width - self.column_gap) / 2

        # Пути
        self.output_path = Path(
            settings.WWW_PATH,
            "temp",
            "teacher-reports",
            f"{self.teacher_id}.pdf",
        )

        # Регистрация шрифтов
        pdfmetrics.registerFont(
            TTFont("DejaVuSans", f"{settings.RESOURCES_PATH}/DejaVuSans.ttf")
        )
        pdfmetrics.registerFont(
            TTFont("DejaVuSans-Bold", f"{settings.RESOURCES_PATH}/DejaVuSans-Bold.ttf")
        )

        # Стили
        self.title_style = ParagraphStyle(
            "StudentTitle",
            fontName="DejaVuSans-Bold",
            fontSize=8.5,
            leading=10,
            alignment=TA_CENTER,
        )

        self.cell_style = ParagraphStyle(
            "Cell",
            fontName="DejaVuSans",
            fontSize=7.5,
            leading=9,
        )

        self.subject_style = ParagraphStyle(
            "Subject",
            parent=self.cell_style,
            fontName="DejaVuSans-Bold",
        )

        self.title_rating_style = ParagraphStyle(
            "RatingTitle",
            parent=self.title_style,
            fontSize=13.5,
            leading=16,
        )

        self.rating_style = ParagraphStyle(
            "Rating",
            parent=self.cell_style,
            fontSize=12,
            leading=14.5,
        )

        self.person_in_rating_style = ParagraphStyle(
            "PersonInRating",
            parent=self.rating_style,
            fontName="DejaVuSans-Bold",
        )

    def _setup_table_style(self, table: Table):
        table.setStyle(TableStyle([
            ("GRID", (0, 0), (-1, -1), 0.4, colors.grey),
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#E8E8E8")),
            ("LEFTPADDING", (0, 0), (-1, -1), 3),
            ("RIGHTPADDING", (0, 0), (-1, -1), 3),
            ("TOPPADDING", (0, 0), (-1, -1), 2),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
        ]))

    @staticmethod
    def _setup_container_style(table: Table):
        table.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))

    def _make_student_table(
        self,
        student_name: str,
        mark_by_subjects: dict[str, tuple[list[str], list[str], list[str]]],
    ) -> Table:
        title = Paragraph(student_name, self.title_style)

        rows = [[
            Paragraph("Предмет", self.subject_style),
            Paragraph("Оценки", self.subject_style),
            *([Paragraph("Ср. балл", self.subject_style)] if self.average else []),
            *([Paragraph("Итог", self.subject_style)] if self.period_marks else []),
        ]]

        for subject, (marks, avg_mark, period_mark) in mark_by_subjects.items():
            if not self.without_marks and not marks:
                continue

            rows.append([
                Paragraph(str(subject), self.subject_style),
                Paragraph(", ".join(str(mark) for mark in marks), self.cell_style),
                *([Paragraph(str(avg_mark[0]), self.cell_style)] if self.average else []),
                *([Paragraph(str(period_mark[0]), self.cell_style)] if self.period_marks else []),
            ])

        if self.signature_lines:
            rows.extend([
                [Paragraph("Подпись классного руководителя: ____________________", self.cell_style)],
                [Paragraph("Подпись родителя: ____________________", self.cell_style)],
            ])

        subject_width = self.table_width * 0.3
        marks_width = self.table_width * 0.49
        avg_mark_width = self.table_width * 0.11
        period_mark_width = self.table_width * 0.1

        if not self.average:
            marks_width += avg_mark_width
        if not self.period_marks:
            marks_width += period_mark_width

        table = self.WatermarkedTable(
            rows,
            colWidths=[
                subject_width,
                marks_width,
                *([avg_mark_width] if self.average else []),
                *([period_mark_width] if self.period_marks else []),
            ],
            repeatRows=1,
            hAlign="LEFT",
        )

        self._setup_table_style(table)

        if self.signature_lines:
            table.setStyle(TableStyle([
                ("SPAN", (0, -2), (-1, -2)),
                ("SPAN", (0, -1), (-1, -1)),
            ]))

        result = Table(
            [[title], [table]],
            colWidths=[self.table_width],
        )

        self._setup_container_style(result)

        return result

    def _make_student_row(self, pair: list[tuple[str, dict]]) -> Table:
        left = self._make_student_table(*pair[0])

        right = (
            self._make_student_table(*pair[1])
            if len(pair) > 1
            else ""
        )

        row = Table(
            [[left, Spacer(self.column_gap, 0), right]],
            colWidths=[
                self.table_width,
                self.column_gap,
                self.table_width,
            ],
        )

        self._setup_container_style(row)

        row.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))

        return row

    def _make_rating_table(self) -> KeepTogether:
        title = Paragraph(
            "Общий рейтинг в классе",
            self.title_rating_style,
        )

        rows = [[
            Paragraph("Место", self.person_in_rating_style),
            Paragraph("Обучающийся", self.person_in_rating_style),
            Paragraph("Ср. балл", self.person_in_rating_style),
        ]]

        for position, student_name, avg_mark in self.rating:
            rows.append([
                Paragraph(str(position), self.person_in_rating_style),
                Paragraph(student_name, self.rating_style),
                Paragraph(str(avg_mark).replace(".", ","), self.rating_style),
            ])

        table = self.WatermarkedTable(
            rows,
            colWidths=[
                self.available_width * 0.1,
                self.available_width * 0.75,
                self.available_width * 0.15,
            ],
            repeatRows=1,
            hAlign="LEFT",
        )

        self._setup_table_style(table)

        rating_block = Table(
            [[title], [table]],
            colWidths=[self.available_width],
            hAlign="CENTER",
        )

        self._setup_container_style(rating_block)

        rating_block.setStyle(TableStyle([
            ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ]))

        return KeepTogether([rating_block])

    def create_pdf(self) -> Path:
        self.output_path.parent.mkdir(parents=True, exist_ok=True)

        doc = BaseDocTemplate(
            str(self.output_path),
            pagesize=A4,
            leftMargin=self.margin_x,
            rightMargin=self.margin_x,
            topMargin=self.margin_y,
            bottomMargin=self.margin_y,
        )

        frame = Frame(
            self.margin_x,
            self.margin_y,
            self.available_width,
            self.page_height - 2 * self.margin_y,
            id="normal",
        )

        doc.addPageTemplates([
            PageTemplate(id="A4", frames=[frame]),
        ])

        story = []

        for i in range(0, len(self.data), 2):
            pair = self.data[i:i + 2]

            story.append(
                KeepTogether([
                    self._make_student_row(pair),
                    Spacer(1, 3 * mm),
                ])
            )

        if self.rating is not None:
            story.append(self._make_rating_table())

        doc.build(story)

        return self.output_path
