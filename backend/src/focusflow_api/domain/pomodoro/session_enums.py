from enum import Enum


class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    ABANDONED = "abandoned"


class SessionEvent(str, Enum):
    REGISTER_INTERVAL = "register_interval"
    COMPLETE_SESSION = "complete_session"
    QUIT_SESSION = "quit_session"
    EXPIRE_SESSION = "expire_session"
