from fastapi import HTTPException
import requests
from config import settings


def test_app(app_id: str, token: str):
    response = requests.post(
        settings.fs_compiler_service_url + "/test", headers={"Authorization": token}, data={"appId": app_id}
    )
    result = response.json()

    if result["exitCode"] == 0:
        # TODO - test result in success
        print("success")
    return result
