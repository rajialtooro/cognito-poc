import datetime
import requests
import json
import sys
from config import settings
from services.solution_checker import (
    get_challenge_data,
    combine_solution_and_tests,
    calling_free_code_orchestrator,
)
from models.Assignment import Assignment
from models.AssignmentData import AssignmentData


def check_assignment_solution(
    assignment: Assignment, assignment_data: AssignmentData, authorization
):
    # * Getting the challenges from the Database based on the IDs we received
    challenges_data = get_challenges_data(assignment["assignmentChallenges"])
    # * Creating a list of challenge IDs from the challengeObjects we have
    challenge_ids = map_challenge_data_to_ids(challenges_data)
    # * Getting the user's submitted solutions
    submissions_data = get_user_assignment_submissions(
        assignment_data, challenge_ids, authorization
    )
    # * Creating an array of all of the student-solution with the testing code
    submissions_compiler_code = get_submissions_with_compiler_testing_code(
        submissions_data, challenges_data
    )

    assignment_results = []
    for solution, challenge_data, assignment_chall, submission in zip(
        submissions_compiler_code,
        challenges_data,
        assignment["assignmentChallenges"],
        submissions_data,
    ):
        data = calling_free_code_orchestrator(
            solution,
            challenge_data["lang"],
            False,
            challenge_data["input"]
            if "input" in challenge_data and challenge_data["input"] != None
            else "",
        )
        # * Getting the compiler output
        output = (
            data["compiler"]["output"] if data["compiler"]["output"] != None else ""
        )
        solved = True if challenge_data["answer"] == output.strip() else False
        grade = assignment_chall["grade"] if solved else 0
        assignment_results.append(
            {
                "solved": solved,
                "challenge_id": challenge_data["challenge_id"],
                "grade": grade,
                "result": submission["result"],
            }
        )
    submit_assignment_results(
        assignment_results, assignment, assignment_data, authorization
    )


def map_challenge_data_to_ids(challenges_data: list):
    challenege_Ids = []
    for challenge in challenges_data:
        challenege_Ids.append(challenge["challenge_id"])
    return challenege_Ids


def get_submissions_with_compiler_testing_code(submissions_data, challenges_data):
    submissions_compiler_code = []
    for user_submission, challenge in zip(submissions_data, challenges_data):
        compiler_code = combine_solution_and_tests(user_submission["result"], challenge)
        submissions_compiler_code.append(compiler_code)
    return submissions_compiler_code


def get_challenges_data(chall_id_arr):
    challenges_data = []
    for challenge in chall_id_arr:
        data = get_challenge_data(
            {"challengeId": challenge["challengeId"], "lang": challenge["lang"]}
        )
        challenges_data.append(data)
    return challenges_data


def get_user_assignment_submissions(
    assignment_data: AssignmentData, challenge_ids: list, authorization
):
    user_submissions = []
    for id in challenge_ids:
        data = get_user_assignment_challenges(assignment_data, id, authorization)
        user_submissions.append(data)
    return user_submissions


# * Route: /courses-svc/courseId/assignments/assignmentId/userId/challengeId)
def get_user_assignment_challenges(
    assignment_data: AssignmentData, challenge_id, authorization
):
    # * using a .env file makes sure that the dev/prod environments are called respectively
    URL = (
        settings.courses_service_url
        + "/{course_id}/assignments/{assignment_id}/{user_id}/{challenge_id}".format(
            course_id=assignment_data.course_id,
            assignment_id=assignment_data.assignment_id,
            user_id=assignment_data.user_id,
            challenge_id=challenge_id,
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


def submit_assignment_results(
    assignment_results: list,
    assignment: Assignment,
    assignment_data: AssignmentData,
    authorization,
):
    submittedAt = str(datetime.datetime.now())
    status = "submitted"
    grade_total = 0
    for challenge_result in assignment_results:
        URL = settings.courses_service_url + "/{course_id}/assignments/{assignment_id}/{user_id}/{challenge_id}/submit".format(
            course_id=assignment_data.course_id,
            assignment_id=assignment_data.assignment_id,
            user_id=assignment_data.user_id,
            challenge_id=challenge_result["challenge_id"],
        )
        grade = int(challenge_result["grade"])
        body = {
            "result": challenge_result["result"],
            "submittedAt": submittedAt,
            "status": status,
            "grade": grade,
        }
        print(body)
        grade_total += grade
        # * Sending get request and saving the response as response object
        data = {}
        try:
            result = requests.post(
                url=URL,
                params=None,
                json=body,
                headers={"Authorization": authorization},
            )
            # * Parsing the data as JSON
            data = result.json()
        except ValueError:
            # * Throwing an error if the challenges-service returned an error
            print("Decoding JSON has failed", data, result)
            raise SystemExit(sys.exc_info()[0])
    submit_user_assignment(assignment_data, grade_total, submittedAt, authorization)


# Call submit user assignment, status="submitted" and date, grade= sum of challenge grades
def submit_user_assignment(
    assignment_data: AssignmentData, grade: int, submittedAt: str, authorization: str
):
    URL = (
        settings.courses_service_url
        + "/{course_id}/assignments/{assignment_id}/{user_id}/submit".format(
            course_id=assignment_data.course_id,
            assignment_id=assignment_data.assignment_id,
            user_id=assignment_data.user_id,
        )
    )
    grade = int(grade)
    body = {
        "submittedAt": submittedAt,
        "status": "submitted",
        "grade": grade,
    }
    print(body)
    # * Sending get request and saving the response as response object
    try:
        result = requests.post(
            url=URL, params=None, json=body, headers={"Authorization": authorization}
        )
        # * Parsing the data as JSON
        data = result.json()
        print("Chekced successfully", data)
    except ValueError:
        # * Throwing an error if the challenges-service returned an error
        print("Decoding JSON has failed", data)
        raise SystemExit(sys.exc_info())
