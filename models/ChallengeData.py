from pydantic import BaseModel
from typing import Optional


class ChallengeData(BaseModel):
    lang: str
    code: str
    challengeId: str
    courseId: Optional[str]
    toSubmit: Optional[bool]
