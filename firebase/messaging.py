from time import time
from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, HttpUrl

from async_firebase.messages import Message as FCMMessage
from async_firebase import AsyncFirebaseClient, FCMBatchResponse


__all__ = ['send_notifications', 'FirebaseApiError', 'Notification', 'AppNotificationChannel']

client = AsyncFirebaseClient()
client.creds_from_service_account_file('firebase-adminsdk.json')


class FirebaseApiError(Exception):
    """Ошибка при отправке запроса в Firebase"""


class AppNotificationChannel(Enum):
    """Возможные каналы уведомлений в приложении"""

    extracurricular_activities = 'extracurricular_activities'
    marks = 'marks'
    service = 'service'
    praise = 'praise'
    notes = 'notes'


class Notification(BaseModel):
    """Уведомление с требуемыми параметрами"""

    firebase_token: str
    """Firebase-токен для отправки уведомления на конкретное устройство"""
    image: Optional[HttpUrl] = None
    """Ссылка на картинку для показа в уведомлении"""
    title: str
    """Заголовок уведомления"""
    message: str
    """Текст (тело) уведомления"""
    channel: AppNotificationChannel
    """Канал уведомления"""
    data: dict[str, Any] = {}
    """Дополнительные данные для передачи на устройство (значения будут представлены в виде строки)"""


async def send_notifications(notifications: list[Notification]) -> FCMBatchResponse:
    """
    Отправка списка уведомлений одним запросом

    :param notifications: список уведомлений
    :return: FCMBatchResponse с данными о кол-ве успешных отправок, ошибок
    :raise FirebaseApiError: ошибка при **отправке** запроса в Firebase
    """

    # Уведомление передается как данные
    # Клиент сам создает и показывает уведомление
    messages = [FCMMessage(
        token=notification.firebase_token,
        data=(data := notification.data.copy()).update(
            channelId=notification.channel.value,
            title=notification.title,
            body=notification.message,
            time=str(int(time() * 1000)),  # Время, которое будет указано в уведомлении
            imageUrl=str(notification.image) if notification.image else None,  # Ссылка на картинку, загрузится клиентом
        ) or data
    ) for notification in notifications]

    try:
        response = await client.send_each(messages)
        return response
    except Exception as e:
        raise FirebaseApiError(e)
