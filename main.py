import requests, json
from fastapi import FastAPI, Header
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models.ChallengeData import ChallengeData
from services.solution_checker import check_solution
from services.get_user_id import get_current_user_id

# * Initial app as a fastapi instance
app = FastAPI()

# * allow cors
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# * Default path to test if service is UP
@app.get("/solution-orch", description="root route of the service")
def root():
    return "{} Service, env: {}".format(settings.app_name, settings.py_env)


# * POST request to run the "checking-solution" flow
@app.post("/solution-orch")
def check_solution_controller(
    challenge_data: ChallengeData, authorization: Optional[str] = Header(None)
):
    # * getting user id from the headers
    userId = get_current_user_id(authorization)
    return check_solution(challenge_data, userId)
