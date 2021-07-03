import requests
import json
import sys
from config import settings
from models.Assignment import Assignment
from models.AssignmentData import AssignmentData

# * Route: /courses-svc/courseId/assignments/assignmentId
def get_assignment(assignment_data: AssignmentData, authorization) -> Assignment:
    # * using a .env file makes sure that the dev/prod environments are called respectively
    URL = (
        settings.courses_service_url
        + "/{course_id}/assignments/{assignment_id}".format(
            course_id=assignment_data.course_id,
            assignment_id=assignment_data.assignment_id,
        )
    )
    data = {}
    # * Sending get request and saving the response as response object
    try:
        result = requests.get(
            url=URL, params=None, headers={"Authorization": authorization}
        )
        # * Parsing the data as JSON
        data = result.json()
    except ValueError:
        # * Throwing an error if the challenges-service returned an error
        print("Decoding JSON has failed", data)
        raise SystemExit(sys.exc_info()[0])
    return data["data"]
