from services.test_app import test_app
import requests
import json
from fastapi import FastAPI, Header, BackgroundTasks
from typing import Optional
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models.ChallengeData import ChallengeData
from models.AssignmentData import AssignmentData
from services.solution_checker import check_solution
from services.assignment_solution_checker import check_assignment_solution
from services.get_user_id import get_current_user_id
from API.get_assignment import get_assignment

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


# * POST request to run the assignment checking flow
@app.post("/solution-orch/assignment/submit", status_code=200)
def check_assignment_controller(
    assignment_data: AssignmentData,
    background_tasks: BackgroundTasks,
    authorization: Optional[str] = Header(None),
):
    assignment = get_assignment(assignment_data, authorization)
    background_tasks.add_task(
        check_assignment_solution, assignment, assignment_data, authorization
    )
    return {"result": "Solution is being checked"}

# * POST request to run the app testing flow


@app.post("/solution-orch/app/test", status_code=200)
def test_app_controller(
    app_id: str,
    authorization: Optional[str] = Header(None),
):
    # * getting user id from the headers
    userId = get_current_user_id(authorization)
    result = test_app(app_id, authorization)
    # TODO - store results
    return result
