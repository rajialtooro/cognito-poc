from services.get_current_user import get_current_user


def get_user_id(user: dict):
    return user["user"]["sub"]


def get_current_user_id(token: str):
    user = get_current_user(token)
    return get_user_id(user)
