from pydantic import BaseModel
from typing import Optional


class UserChallengeData(BaseModel):
    time_spent: int
    coding_time: int
    time_out_tab: int
    error: str   

class AssignmentData(BaseModel):
    course_id: str
    assignment_id: str
    user_id: str
    challenges_data: dict
