from enum import Enum
from typing import Optional, Any

from pydantic import BaseModel, HttpUrl

from async_firebase import AsyncFirebaseClient
from async_firebase.messages import Message as FCMMessage, Notification as FCMNotification, AndroidConfig


__all__ = ['send_notifications', 'FirebaseApiError', 'Notification', 'AppNotificationChannel']

client = AsyncFirebaseClient()
client.creds_from_service_account_file('firebase-adminsdk.json')


class FirebaseApiError(Exception):
    pass


class AppNotificationChannel(Enum):
    extracurricular_activities = 'extracurricular_activities'
    marks = 'marks'
    service = 'service'
    praise = 'praise'


class Notification(BaseModel):
    firebase_token: str
    image: Optional[HttpUrl] = None
    title: str
    message: str
    channel: AppNotificationChannel
    data: dict[str, Any] = {}


async def send_notifications(notifications: list[Notification]):
    messages = [FCMMessage(
        notification=FCMNotification(
            title=notification.title,
            body=notification.message,
            image=str(notification.image)
        ),
        token=notification.firebase_token,
        android=AndroidConfig.build(
            priority='high',
            channel_id=notification.channel.value,
            data=notification.data
        )
    ) for notification in notifications]

    try:
        response = await client.send_each(messages)
        print(response)
    except Exception as e:
        raise FirebaseApiError(e)
