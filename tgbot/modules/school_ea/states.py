from aiogram.fsm.state import StatesGroup, State


__all__ = ['ExtracurricularActivitiesStatesGroup']


class ExtracurricularActivitiesStatesGroup(StatesGroup):
    """Группа состояний при изменении внеурочных занятий в образовательной организации"""

    update_extracurricular_activity = State('update_extracurricular_activity')
    """Ожидание сообщения от Web Mini App с данными об обновленном внеурочном занятии"""

    create_extracurricular_activities = State('create_extracurricular_activities')
    """Ожидание сообщения от Web Mini App с данными о созданных внеурочных занятиях"""