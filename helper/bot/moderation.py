from datetime import datetime, timedelta
from typing import Dict

BLOCKED_USERS: Dict[int, datetime] = {}  # user_id: until_time
LAST_MESSAGE_TIME: Dict[int, datetime] = {}  # user_id: last_message_time

RATE_LIMIT_SECONDS = 20


def block_user(user_id: int, minutes: int = 60):
    """Блокирует пользователя на заданное количество минут."""
    BLOCKED_USERS[user_id] = datetime.now() + timedelta(minutes=minutes)


def unblock_user(user_id: int):
    """Разблокирует пользователя вручную."""
    BLOCKED_USERS.pop(user_id, None)


def is_user_blocked(user_id: int) -> bool:
    """Проверяет, заблокирован ли пользователь. Если срок истёк — удаляет из списка."""
    unblock_time = BLOCKED_USERS.get(user_id)
    if unblock_time:
        if datetime.now() < unblock_time:
            return True
        else:
            del BLOCKED_USERS[user_id]
    return False


def get_blocked_users() -> Dict[int, datetime]:
    """Возвращает словарь текущих заблокированных пользователей."""
    return BLOCKED_USERS


def is_rate_limited(user_id: int) -> bool:
    """Проверка, отправлял ли пользователь сообщение недавно."""
    now = datetime.now()
    last_time = LAST_MESSAGE_TIME.get(user_id)
    if last_time and (now - last_time).total_seconds() < RATE_LIMIT_SECONDS:
        return True
    LAST_MESSAGE_TIME[user_id] = now
    return False
