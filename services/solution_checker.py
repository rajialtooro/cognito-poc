import requests
import json
import sys
from config import settings
from models.ChallengeData import ChallengeData
from utils.sanitize_source_code import sanitize_source_code


# * Method to check if the given solution gives the desired output(answer found in DB), to be considered as "solved"
def check_solution(data: ChallengeData) -> str:
    # * Starting with a dictionary that will be filled with the results of the various requests
    result = {"solved": None, "linter": None, "Compiler": None}
    # * Default value of the variable that represents if the user successfully solved the challenge
    solved = False
    # * Getting the challenge from the Database based on the ID we received
    challengeData = get_challenge_data(data)
    # * Removing any comments or literal strings from the code before looking for the white/black listed words
    sanitized_solution = sanitize_source_code(data.code, challengeData["lang"])
    # * Checking if the solution we received contains the "must-have" words for it to be correct
    if solution_contains_approved_words(
        sanitized_solution, challengeData
    ) and not solution_contains_illegal_words(sanitized_solution, challengeData):
        # * Prepparing the code, by combining the solution, with the test functions(boiler) and extra classes
        compiler_code = combine_solution_and_tests(data.code, challengeData)
        # * Calling the Free-Coding-Orchestrator to run the Compiler and Analyer(Linter), and combine the results
        result = run_compiler_and_analyzer(compiler_code, data.lang)
        # * Getting the compiler output
        output = result["compiler"]["output"]
        solved = True if challengeData["answer"] in output else False
    # * Adding the "solved" key value to True/False, based on what happend above
    result["solved"] = solved
    return result


# * Function to get the "challenge" object from the database
def get_challenge_data(data: ChallengeData):
    # * Setting the URL to call the "challenges-service", which contacts the DB
    # * using a .env file makes sure that the dev/prod environments are called respectively
    URL = settings.challenges_service_url + "/{lang}/{id}".format(
        lang=data.lang, id=data.challengeId
    )
    data = {}
    # * Sending get request and saving the response as response object
    try:
        result = requests.get(url=URL, params=None)
        # * Parsing the data as JSON
        data = result.json()
    except:
        # * Throwing an error if the challenges-service returned an error
        raise SystemExit(sys.exc_info()[0])
    return data


def solution_contains_approved_words(sanitized_solution: str, challengeData):
    return all(word in sanitized_solution for word in challengeData["white_list"])


def solution_contains_illegal_words(sanitized_solution: str, challengeData):
    return any(word in sanitized_solution for word in challengeData["black_list"])


def combine_solution_and_tests(solution: str, challengeData):
    solution_with_tests = (
        challengeData["boiler"].replace("{{code}}", solution)
        if "boiler" in challengeData
        else solution
    )
    solution_with_tests = (
        solution_with_tests.replace("{{classes}}", challengeData["classes"] or "")
        if "classes" in challengeData
        else solution
    )
    if "isMain" in challengeData and not challengeData["isMain"]:
        solution_with_tests = (
            solution_with_tests.replace("{{tests}}", challengeData["tests"] or "")
            if "tests" in challengeData
            else solution
        )
    return solution_with_tests


# * Sending a POST request to the "free-coding-orchestrator" which runs the compiler and analyzer
def run_compiler_and_analyzer(code: str, lang: str):
    # * Creating the body of the request with programming-language(lang), code-to-compile(code), and run-linter(lint)
    # * lint = False, means to not run the Code-Analyzer
    body = {"lang": lang, "code": code, "lint": False}

    # * Setting the URL of the post request to the free-orchestrator, which calls the Compiler and Analyzer(Linter)
    URL = settings.free_orch_url
    # * json.dumps() converts the dictionary(body), to a valid JSON, for example turning "False" to "false"
    DATA = json.dumps(body)
    data = {}
    # * Sending post request and saving the response as response object
    try:
        result = requests.post(url=URL, data=DATA)
        data = result.json()
    except:
        # * Throwing an error if the free-coding-orchestrator failed and returned an error
        raise SystemExit(sys.exc_info()[0])
    return data
