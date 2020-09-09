import requests
import json
import sys
from config import settings
from models.ChallengeData import ChallengeData
from utils.sanitize_source_code import clean_comments, remove_strings


# * Method to check if the given solution gives the desired output(answer found in DB), to be considered as "solved"
def check_solution(data: ChallengeData) -> str:
    # * Starting with a dictionary that will be filled with the results of the various requests
    result = {"solved": None, "feedback": {}, "linter": None, "compiler": None}
    # * Default value of the variable that represents if the user successfully solved the challenge
    solved = False
    # * Getting the challenge from the Database based on the ID we received
    challengeData = get_challenge_data(data)
    # * Getting the feedback messages and boolean flags for white/black listed words
    result_dict = get_solution_feedback_and_flags(data.code, challengeData)
    result["feedback"]["approvedMissing"], result["feedback"]["illegalFound"] = (
        result_dict["missing_msg"],
        result_dict["illegal_msg"],
    )
    is_approved_solution, is_illegal_solution = (
        result_dict["is_approved_solution"],
        result_dict["is_illegal_solution"],
    )
    # * Checking if the solution we received contains the "must-have" words for it to be correct
    if is_approved_solution and not is_illegal_solution:
        # * Prepparing the code, by combining the solution, with the test functions(boiler) and extra classes
        compiler_code = combine_solution_and_tests(data.code, challengeData)
        # * Calling the Free-Coding-Orchestrator to run the Compiler and Analyer(Linter), and combine the results
        compiler_analyzer_result = calling_free_code_orchestrator(
            compiler_code, data.lang
        )
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


# * Method to simplify readability of flow
# * Calls the methods that check if the solution contains all of the white listed words and non of the balck listed words
def get_solution_feedback_and_flags(non_sanitized_solution: str, challengeData):
    # * Removing any comments or literal strings from the code before looking for the white/black listed words
    sol_wo_comments = clean_comments(non_sanitized_solution, challengeData["lang"])
    sol_wo_strings_and_comments = remove_strings(sol_wo_comments)
    result_dict = {}
    (
        result_dict["missing_msg"],
        result_dict["is_approved_solution"],
    ) = solution_contains_approved_words(sol_wo_comments, challengeData)
    (
        result_dict["illegal_msg"],
        result_dict["is_illegal_solution"],
    ) = solution_contains_illegal_words(sol_wo_strings_and_comments, challengeData)
    return result_dict


# * Check if the sanitized solution(without comments and strings) contains all of the words in the white-listed words array
# * Return a custom feedback message and a boolean indicating if words were missing
def solution_contains_approved_words(sanitized_solution: str, challengeData):
    missing_words_set = (
        {word for word in challengeData["white_list"] if word not in sanitized_solution}
        if challengeData["white_list"] is list
        else check_keyword_loopx_challeneges(
            sanitized_solution, challengeData["white_list"]
        )
    )
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


# * A methpd to check for keywords in challenges migrated from older platform
# * A string of key words might look something like this: "for:while;if;next"
# * Words that have ":" between them is equal to "or", so one of them is needed to appear
# * ";" is eqaul to "and" which means all of those should exist within the solution
def check_keyword_loopx_challeneges(code, keywords):
    missing_elements = []
    lowercase_solution = code.lower()
    lowercase_keywords = keywords.lower().split(";")
    for ands in lowercase_keywords:
        found_keyword = False
        for ors in ands.split(":"):
            if ors in lowercase_solution:
                found_keyword = True
        if not found_keyword:
            missing_elements.append(" or ".join(ands.split(":")))
    return missing_elements


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


"""
This method replaces the placeholders with the appropriate values for each:
- {{tests}} --> is replaced by the testing code
- {{code}} --> is replaced by the user's solution
- {{classes}} --> is replaced by any extra classes needed for the tests or the solution to run
"""
"""
* The "boiler" code for Java for example will look like this:
class HelloWorld 
{ 
  public static void main(String args[]) 
  { 
    {{tests}}
  } 
    {{code}}      
}
{{classes}}
"""


def combine_solution_and_tests(solution: str, challengeData):
    # * For Java "Class" exercises specifically, we need to edit the solution slighlty
    solution = (
        edit_java_class_solution(solution)
        if challengeData["lang"] == "java" and solution.strip().startswith("class")
        else solution
    )
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


# * To run and call inner classes in Java within the main method they have to be static
# * We add it here to prevent confusing the user when solving the challenge
def edit_java_class_solution(solution: str):
    return "static " + solution


# * Sending a POST request to the "free-coding-orchestrator" which runs the compiler and analyzer
def calling_free_code_orchestrator(code: str, lang: str):
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
