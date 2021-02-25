from pydantic import BaseModel
from typing import Optional


class Assignment(BaseModel):
    assignmentChallenges: list
    grade: Optional[int]
