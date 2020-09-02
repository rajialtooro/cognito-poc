from pydantic import BaseModel


class ChallengeData(BaseModel):
    lang: str
    code: str
    challengeId: str
