import requests
import json
from config import settings
from models.ChallengeData import ChallengeData


def check_solution(data: ChallengeData) -> str:
    # * Starting with an empty dictionary that will be filled with the results of the various requests
    result = {"solved": False, "linter": None, "Compiler": None}
    # * Default value of the varibale that represents if the user successfully solved the challenge
    solved = False
    # * Unpacking the data object to its seperate attributes for ease of use
    lang, solution_code, chall_id = data.lang, data.code, data.challengeId
    # * Getting the challenge from the Database based on the ID we received
    challengeData = get_challenge_data(chall_id, lang)
    # * Checking if the solution we recieved contains the "must-have" words for it to pass
    # * If it does(True), then we contniue with the flow,
    # * else we leave the default "solved" value to False and do not call the Free-Orchestrator
    if white_labeled_words(solution_code):
        # * Prepparing the code, by combining the solution, with the test functions(boiler)
        compiler_code = solution_code + challengeData["boiler"]
        # * Calling the Free-Coding-Orchestrator to run the Compiler and Analyer(Linter), and combine the results
        result = call_free_orch(compiler_code, lang)
        # * Getting the compiler output
        output = result["compiler"]["output"]
        solved = True if challengeData["answer"] in output else False
    # * Adding the "solved" key value to True/False, based on what happend above
    result["solved"] = solved
    return result


def get_challenge_data(id, lang):
    # * Setting the URL to call the "challenges-service", which contacts the DB
    # * using a .env file makes sure that the dev/prod environments are called respectivily
    URL = settings.challenges_service_url + "/{lang}/{id}".format(lang=lang, id=id)
    data = {}
    # * Sending get request and saving the response as response object
    try:
        result = requests.get(url=URL, params=None)
        # * Parsing the data as JSON
        data = result.json()
    except requests.exceptions.HTTPError as err:
        # * Throwing HTTP error
        raise SystemExit(err)
    return data


# TODO: Add behavior for checking "white-labeled" words
# * Currently(August-31st-2020) no such values exists in the DB
def white_labeled_words(solution: str):
    return True


def call_free_orch(code: str, lang: str):
    # * Creating the body of the request with programming-language(lang), code-to-compile(code), and run-linter(lint)
    # * lint = False, means to not run the Code-Analyer
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
    except requests.exceptions.HTTPError as err:
        # * Throwing HTTP error
        raise SystemExit(err)
    return data
