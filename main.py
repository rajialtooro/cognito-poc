import requests
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from models.ChallengeData import ChallengeData
from services.checkChallenge import checkChallenge

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


@app.get("/solution-orch", description="root route of the service")
def root():
    return "{} Service, env: {}".format(settings.app_name, settings.py_env)


@app.post("/solution-orch")
def checkChalelngeController(challengeData: ChallengeData):
    return checkChallenge()
