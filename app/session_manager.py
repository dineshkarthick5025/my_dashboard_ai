import secrets

# Dictionary to store active sessions in memory (not persistent)
sessions = {}

def create_session(user_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    sessions[session_id] = user_id
    return session_id

def get_user_id(session_id: str) -> int | None:
    return sessions.get(session_id)

def delete_session(session_id: str):
    if session_id in sessions:
        del sessions[session_id]
