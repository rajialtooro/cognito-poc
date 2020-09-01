import requests
import json
import sys
from config import settings
from models.ChallengeData import ChallengeData


# * Method to check if the given solution gives the desired output(answer found in DB), to be considered as "solved"
def check_solution(data: ChallengeData) -> str:
    # * Starting with a dictionary that will be filled with the results of the various requests
    result = {"solved": None, "linter": None, "Compiler": None}
    # * Default value of the varibale that represents if the user successfully solved the challenge
    solved = False
    # * Getting the challenge from the Database based on the ID we received
    challengeData = get_challenge_data(data)
    # * Checking if the solution we recieved contains the "must-have" words for it to be correct
    if solution_contains_approved_words(data.code):
        # * Prepparing the code, by combining the solution, with the test functions(boiler)
        compiler_code = data.code + challengeData["boiler"]
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
    # * using a .env file makes sure that the dev/prod environments are called respectivily
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


# TODO: Add behavior for checking "white-labeled" words
# * Currently(August-31st-2020) no such values exists in the DB
def solution_contains_approved_words(solution: str):
    return True


# * Sending a POST request to the "free-coding-orchestrator" which runs the compiler and analyzer
def run_compiler_and_analyzer(code: str, lang: str):
    # * Creating the body of the request with programming-language(lang), code-to-compile(code), and run-linter(lint)
    # * lint = False, means to not run the Code-Analyzer
    body = {"lang": lang, "code": code, "lint": False}

    # * Setting the URL of the post request to the free-orchestrator, which calls the Compiler and Analyzer(Linter)
    URL = settings.free_orch_url
    # * json.dumps() converts the dictionary(body), to a valid JSON, for example truning "False" to "false"
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
