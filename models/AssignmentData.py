from pydantic import BaseModel
from typing import Optional


class AssignmentData(BaseModel):
    course_id: str
    assignment_id: str
    user_id: str
