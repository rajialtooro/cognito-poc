import requests
import json
import sys
from config import settings
from models.ChallengeData import ChallengeData
from utils.sanitize_source_code import sanitize_source_code


# * Method to check if the given solution gives the desired output(answer found in DB), to be considered as "solved"
def check_solution(data: ChallengeData) -> str:
    # * Starting with a dictionary that will be filled with the results of the various requests
    result = {"solved": None, "feedback": {}, "linter": None, "compiler": None}
    # * Default value of the variable that represents if the user successfully solved the challenge
    solved = False
    # * Getting the challenge from the Database based on the ID we received
    challengeData = get_challenge_data(data)
    # * Removing any comments or literal strings from the code before looking for the white/black listed words
    sanitized_solution = sanitize_source_code(data.code, challengeData["lang"])
    # * Getting the feedback messages and boolean flags for white/black listed words
    (
        result["feedback"]["approvedMissing"],
        is_approved_solution,
    ) = solution_contains_approved_words(sanitized_solution, challengeData)
    (
        result["feedback"]["illegalFound"],
        is_illegal_solution,
    ) = solution_contains_illegal_words(sanitized_solution, challengeData)
    # * Checking if the solution we received contains the "must-have" words for it to be correct
    if is_approved_solution and not is_illegal_solution:
        # * Prepparing the code, by combining the solution, with the test functions(boiler) and extra classes
        compiler_code = combine_solution_and_tests(data.code, challengeData)
        # * Calling the Free-Coding-Orchestrator to run the Compiler and Analyer(Linter), and combine the results
        compiler_analyzer_result = run_compiler_and_analyzer(compiler_code, data.lang)
        result["linter"], result["compiler"] = (
            compiler_analyzer_result["linter"],
            compiler_analyzer_result["compiler"],
        )
        # * Getting the compiler output
        output = result["compiler"]["output"]
        solved = True if challengeData["answer"] == output.strip() else False
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


# * Check if the sanitized solution(without comments and strings) contains all of the words in the white-listed words array
# * Return a custom feedback message and a boolean indicating if words were missing
def solution_contains_approved_words(sanitized_solution: str, challengeData):
    missing_words_set = {
        word for word in challengeData["white_list"] if word not in sanitized_solution
    }
    feedback_msg = (
        "Your code is missing some key-elements, like: {0}".format(
            ", ".join(missing_words_set)
        )
        if missing_words_set
        else "Code contains all key elements"
    )
    return (
        feedback_msg,
        not bool(missing_words_set),
    )


# * Check if the sanitized solution(without comments and strings) contains any word from the black-list array
# * Return a custom feedback message and a boolean indicating if any words were found
def solution_contains_illegal_words(sanitized_solution: str, challengeData):
    illegal_words_set = {
        word for word in challengeData["black_list"] if word in sanitized_solution
    }
    feedback_msg = (
        "Your code is contains some terms that are not allowed, like: {0}".format(
            ", ".join(illegal_words_set)
        )
        if illegal_words_set
        else ""
    )
    return (feedback_msg, bool(illegal_words_set))


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
    if "is_main" in challengeData and not challengeData["is_main"]:
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
