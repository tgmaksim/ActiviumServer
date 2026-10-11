import secrets

from pathlib import Path
from asyncio import gather
from datetime import datetime, UTC
from typing import Optional, Callable, Union

from yarl import URL
from httpx import AsyncClient

from dnevnikru import AioDnevnikruApi, DnevnikruApiException

from ...config.project_config import settings
from ...repositories.log_uow import LogUnitOfWork
from ...services.html_response import HtmlResponse
from ...repositories.statistic_repository import StatName

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
                    school: dict = next(filter(lambda s: s['type'] in ('Regular', 'Professional') and s['id'] in schools_id, schools))
                    school_id = int(school['id'])

                    groups = await dnr.get_school_groups(school_id)
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
                            'name': group['name'],
                            'groupId': group['id']
                        }
                        for group in groups
                    ]

        if not authorized:
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
                    'max_age': 30 * 24 * 60 * 60,  # 30 дней
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
                    'max_age': 30 * 24 * 60 * 60,
                    'httponly': True,
                    'samesite': 'lax'
                }
            ]
        )

    async def create_report(self, session_id: str, group_id: int) -> Union[tuple[Path, str], HtmlResponse]:
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
                    'max_age': 30 * 24 * 60 * 60,
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
            group, periods, _persons, _subjects = await gather(
                dnr.get_group(group_id),
                dnr.get_reporting_periods(group_id),
                dnr.get_group_persons(group_id),
                dnr.get_subjects(group_id)
            )
        except DnevnikruApiException:
            if not await uow.teacher_session_repository.check_session_auth(session_id, dnr):
                return root_result
            raise

        persons = {person['id']: person['shortName'] for person in _persons}
        subjects = {subject['id']: subject['name'] for subject in _subjects}

        periods = sorted(periods, key=lambda p: datetime.fromisoformat(p['start']))
        active_period = CacheService.get_active_period(periods, datetime.now(UTC).date())

        marks = await dnr.get_group_marks(group_id, active_period['start'], active_period['finish'])
        marks_by_person_id_subject: dict[int, dict[str, list[str]]] = {}

        works_ids = {mark['work'] for mark in marks}
        _works = await dnr.get_works(list(works_ids))
        works = {work['id']: work for work in _works}

        for mark in marks:
            if marks_by_person_id_subject.get(mark['person']) is None:
                marks_by_person_id_subject[mark['person']] = {subject: [] for subject in subjects.values()}

            subject = subjects[works[mark['work']]['subjectId']]
            marks_by_person_id_subject[mark['person']][subject].append(mark['textValue'])

        marks_by_person_subject: list[tuple[str, dict[str, list[str]]]] = [
            (person_name, marks_by_person_id_subject.get(person_id, {subject: [] for subject in subjects.values()}))
            for person_id, person_name in persons.items()
        ]

        pdf = self._create_pdf(session.teacher_id, marks_by_person_subject)

        async with self.uow_factory() as uow:
            await uow.statistic_repository.add_statistic(session.teacher_id, StatName.teacherCreateReport)

        return pdf, group['fullName']

    @staticmethod
    def _create_pdf(teacher_id: int, data: list[tuple[str, dict[str, list[str]]]]) -> Path:
        pdfmetrics.registerFont(
            TTFont("DejaVuSans", f"{settings.RESOURCES_PATH}/DejaVuSans.ttf")
        )

        pdfmetrics.registerFont(
            TTFont("DejaVuSans-Bold", f"{settings.RESOURCES_PATH}/DejaVuSans-Bold.ttf")
        )

        output_path = Path(settings.WWW_PATH, 'temp', 'teacher-reports', f"{teacher_id}.pdf")

        # Размер страницы A4
        page_width, page_height = A4

        # Отступы страницы
        margin_x = 10 * mm
        margin_y = 10 * mm

        # Между двумя таблицами в одном ряду
        column_gap = 4 * mm

        # Доступная ширина
        available_width = page_width - 2 * margin_x

        # Ширина одной таблицы
        table_width = (available_width - column_gap) / 2

        title_style = ParagraphStyle(
            "StudentTitle",
            fontName="DejaVuSans-Bold",
            fontSize=8.5,
            leading=10,
            alignment=TA_CENTER,
            spaceAfter=0,
        )

        cell_style = ParagraphStyle(
            "Cell",
            fontName="DejaVuSans",
            fontSize=7.5,
            leading=9,
            spaceAfter=0,
            spaceBefore=0,
        )

        subject_style = ParagraphStyle(
            "Subject",
            parent=cell_style,
            fontName="DejaVuSans-Bold",
        )

        def make_student_table(
            student_name: str,
            subjects: dict[str, list[str]],
        ) -> Table:
            # Заголовок таблицы
            title = Paragraph(
                student_name,
                title_style,
            )

            rows = [
                [
                    Paragraph("<b>Предмет</b>", cell_style),
                    Paragraph("<b>Оценки</b>", cell_style),
                ]
            ]

            for subject, marks in subjects.items():
                # Оценки в одну строку
                marks_text = ", ".join(str(mark) for mark in marks)

                rows.append(
                    [
                        Paragraph(
                            str(subject),
                            subject_style,
                        ),
                        Paragraph(
                            marks_text,
                            cell_style,
                        ),
                    ]
                )

            # Ширина столбцов
            # Первый столбец немного шире, чтобы названия предметов реже переносились
            subject_width = table_width * 0.42
            marks_width = table_width * 0.58

            table = Table(
                rows,
                colWidths=[subject_width, marks_width],
                repeatRows=1,
                hAlign="LEFT",
            )

            table.setStyle(
                TableStyle(
                    [
                        # Границы
                        (
                            "GRID",
                            (0, 0),
                            (-1, -1),
                            0.4,
                            colors.grey,
                        ),

                        # Фон заголовка
                        (
                            "BACKGROUND",
                            (0, 0),
                            (-1, 0),
                            colors.HexColor("#E8E8E8"),
                        ),

                        # Отступы внутри ячеек
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            3,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            3,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            2,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            2,
                        ),

                        # Вертикальное выравнивание
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),

                        # Выравнивание заголовков
                        (
                            "ALIGN",
                            (0, 0),
                            (-1, 0),
                            "CENTER",
                        ),
                    ]
                )
            )

            # Заголовок ученика и сама таблица
            result = Table(
                [
                    [title],
                    [table],
                ],
                colWidths=[table_width],
            )

            result.setStyle(
                TableStyle(
                    [
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                    ]
                )
            )

            return result

        doc = BaseDocTemplate(
            str(output_path),
            pagesize=A4,
            leftMargin=margin_x,
            rightMargin=margin_x,
            topMargin=margin_y,
            bottomMargin=margin_y,
        )

        frame = Frame(
            margin_x,
            margin_y,
            page_width - 2 * margin_x,
            page_height - 2 * margin_y,
            id="normal",
        )

        doc.addPageTemplates(
            [
                PageTemplate(
                    id="A4",
                    frames=[frame],
                )
            ]
        )

        story = []

        for i in range(0, len(data), 2):
            pair = data[i:i + 2]

            tables = []

            for student_name, subjects in pair:
                tables.append(
                    make_student_table(
                        student_name,
                        subjects,
                    )
                )

            tables.insert(1, Spacer(10, 0))

            # Если в последнем ряду только один ученик, вторая половина пустая
            if len(tables) == 1:
                tables.append("")

            row = Table(
                [tables],
                colWidths=[
                    table_width,
                    10,
                    table_width,
                ],
            )

            row.setStyle(
                TableStyle(
                    [
                        (
                            "LEFTPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "RIGHTPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "TOPPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "BOTTOMPADDING",
                            (0, 0),
                            (-1, -1),
                            0,
                        ),
                        (
                            "VALIGN",
                            (0, 0),
                            (-1, -1),
                            "TOP",
                        ),
                    ]
                )
            )

            story.append(
                KeepTogether(
                    [
                        row,
                        Spacer(1, 3 * mm),
                    ]
                )
            )

        doc.build(story)

        return output_path
