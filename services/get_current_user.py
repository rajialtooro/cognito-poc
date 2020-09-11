from fastapi import HTTPException
import requests
from config import settings


def get_current_user(token: str):
    if not token:
        raise HTTPException(status_code=401, detail="Not logged in")
    response = requests.post(
        settings.auth_service_url + "/isloggedin", headers={"Authorization": token}
    )
    user = response.json()

    if not user["isLoggedIn"]:
        raise HTTPException(status_code=401, detail="Not logged in")
    return user
