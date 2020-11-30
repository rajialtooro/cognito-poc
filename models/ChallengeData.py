from pydantic import BaseModel
from typing import Optional


class ChallengeData(BaseModel):
    lang: str
    code: str
    challengeId: str
    courseId: Optional[str]
    toSubmit: Optional[bool]
    time_spent: Optional[int] = 0
    lint: Optional[bool] = False
