from datetime import datetime, timedelta
from typing import Dict

BLOCKED_USERS: Dict[str, datetime] = {}  # username.lower(): until_time
LAST_MESSAGE_TIME: Dict[str, datetime] = {}  # username.lower(): last_message_time

RATE_LIMIT_SECONDS = 20


def block_user(username: str, minutes: int = 60):
    """Блокирует пользователя на заданное количество минут."""
    BLOCKED_USERS[username.lower()] = datetime.now() + timedelta(minutes=minutes)


def unblock_user(username: str):
    """Разблокирует пользователя вручную."""
    BLOCKED_USERS.pop(username.lower(), None)


def is_user_blocked(username: str) -> bool:
    """Проверяет, заблокирован ли пользователь. Если срок истёк — удаляет из списка."""
    username = username.lower()
    unblock_time = BLOCKED_USERS.get(username)
    if unblock_time:
        if datetime.now() < unblock_time:
            return True
        else:
            del BLOCKED_USERS[username]
    return False


def get_blocked_users() -> Dict[str, datetime]:
    """Возвращает словарь текущих заблокированных пользователей."""
    return BLOCKED_USERS


def is_rate_limited(username: str) -> bool:
    """Проверка, отправлял ли пользователь сообщение недавно."""
    username = username.lower()
    now = datetime.now()
    last_time = LAST_MESSAGE_TIME.get(username)
    if last_time and (now - last_time).total_seconds() < RATE_LIMIT_SECONDS:
        return True
    LAST_MESSAGE_TIME[username] = now
    return False
