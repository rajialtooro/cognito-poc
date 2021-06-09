import re

import requests
import json
import sys
from config import settings
from models.ChallengeData import ChallengeData
from models.constants import correct_patterns
from utils.sanitize_source_code import clean_comments, remove_strings


# * Method to check if the given solution gives the desired output(answer found in DB), to be considered as "solved"
def check_solution(data: ChallengeData, userId: str) -> str:
    # * Starting with a dictionary that will be filled with the results of the various requests
    result = {"solved": None, "feedback": {}, "linter": {}, "compiler": ""}
    # * Default value of the variable that represents if the user successfully solved the challenge
    solved = False
    # * Getting the challenge from the Database based on the ID we received
    challengeData = get_challenge_data(data)
    # * Checks capitalization
    # * Getting the feedback messages and boolean flags for white/black listed words
    result_dict = get_solution_feedback_and_flags(data.code, challengeData)
    result["feedback"]["approvedMissing"], result["feedback"]["illegalFound"], result["linter"] = (
        result_dict["missing_msg"],
        result_dict["illegal_msg"],
        result_dict["violations"],
    )
    is_approved_solution, is_illegal_solution = (
        result_dict["is_approved_solution"],
        result_dict["is_illegal_solution"],
    )
    # * If there are capitalization violations doesn't compile and analyze code
    if result["linter"]["violations"]:
        return result
    # * Checking if the solution we received contains the "must-have" words for it to be correct
    if is_approved_solution and not is_illegal_solution:
        # * Prepparing the code, by combining the solution, with the test functions(boiler) and extra classes
        compiler_code = combine_solution_and_tests(data.code, challengeData)
        # * Calling the Free-Coding-Orchestrator to run the Compiler
        #  and Analyer(Linter), and combine the results
        compiler_analyzer_result = calling_free_code_orchestrator(
            compiler_code,
            data.lang,
            data.lint,
            challengeData["input"] if challengeData["input"] != None else "",
        )
        result["linter"], result["compiler"] = (
            compiler_analyzer_result["linter"]
            if compiler_analyzer_result["linter"] != None
            else {"violations": []},
            compiler_analyzer_result["compiler"],
        )
        result["linter"]["violations"] = (
            update_linter_line_values(
                result["linter"]["violations"],
                compiler_code,
                data,
                challengeData,
            )
            if result["linter"]["violations"] != None
            else result["linter"]
        )
        # * Getting the compiler output
        output = (
            result["compiler"]["output"] if result["compiler"]["output"] != None else ""
        )
        solved = True if challengeData["answer"] == output.strip() else False
    # * Adding the "solved" key value to True/False, based on what happend above
    result["solved"] = solved

    if data.courseId:
        saving_user_challenge_data(
            data,
            userId,
            solved,
        )
    return result


def update_linter_line_values(
        violations, solution_with_tests, user_submission: ChallengeData, complete_challenge_data
):
    challenge_code_lst = user_submission.code.split("\n")
    challenge_code_lst_length = len(challenge_code_lst)
    is_main = complete_challenge_data["is_main"]
    if (
            user_submission.lang == "c"
            or user_submission.lang == "cs"
            or user_submission.lang == "java"
    ) and not is_main:
        sol_start_line = calc_line_diff(user_submission, solution_with_tests)
        sol_end_line = sol_start_line + challenge_code_lst_length - 1
        for violation in list(violations):
            if violation["line"] < sol_start_line or violation["line"] > sol_end_line:
                violations.remove(violation)
        for violation in violations:
            violation["line"] = violation["line"] - sol_start_line
    elif is_main:
        if " main(" in user_submission.code.lower() and user_submission.lang != "c" and " main(" in complete_challenge_data["tests"].lower():
            violations = unnecessary_main_or_class(user_submission, violations)
        else:
            sol_start_line = 0
            for idx, line in enumerate(solution_with_tests.split("\n")):
                if line.strip() == challenge_code_lst[0].strip():
                    sol_start_line = idx
                    break
            sol_end_line = sol_start_line + challenge_code_lst_length - 1
            for violation in list(violations):
                if (
                        violation["line"] < sol_start_line
                        or violation["line"] > sol_end_line
                ):
                    violations.remove(violation)
            for violation in violations:
                violation["line"] = violation["line"] - (sol_start_line + 1)
    return violations


def unnecessary_main_or_class(challenge_data: ChallengeData, violations):
    code_list = challenge_data.code.lower().split("\n")
    line = 0
    for idx, line in enumerate(code_list):
        if "main" in line:
            line = idx
            break
    violations.clear()
    violations.append(
        {
            "line": line,
            "column": 0,
            "id": "No need to create a 'Main' method, or a class",
        }
    )
    return violations


def calc_line_diff(challenge_data: ChallengeData, solution_with_tests):
    arr_of_new_lines = solution_with_tests.split("\n")
    line_diff = 0
    for line_break in arr_of_new_lines:
        reached_func_name = (
            reached_func_name_curly_brackets(line_break, challenge_data.code)
            if challenge_data.lang in {"java", "cs", "c"}
            else reached_func_name_tabs(line_break, challenge_data.code)
        )
        if reached_func_name:
            break
        line_diff += 1
    return line_diff


def reached_func_name_curly_brackets(sol_with_tests, only_sol):
    return sol_with_tests.split("{")[0].strip() == only_sol.split("{")[0].strip()


def reached_func_name_tabs(sol_with_tests, only_sol):
    return sol_with_tests.split(":")[0].strip() == only_sol.split(":")[0].strip()


# * Function to get the "challenge" object from the database
def get_challenge_data(data: ChallengeData):
    # * Setting the URL to call the "challenges-service", which contacts the DB
    # * using a .env file makes sure that the dev/prod environments are called respectively
    URL = (
        settings.challenges_service_url
        + "/challenges/{id}?lang={lang}".format(lang=data.lang, id=data.challengeId)
        if type(data) is ChallengeData
        else settings.challenges_service_url
             + "/challenges/{id}?lang={lang}".format(
            lang=data["lang"], id=data["challengeId"]
        )
    )
    data = {}
    # * Sending get request and saving the response as response object
    try:
        result = requests.get(url=URL, params=None)
        # * Parsing the data as JSON
        data = result.json()
    except ValueError:
        # * Throwing an error if the challenges-service returned an error
        raise SystemExit(sys.exc_info()[0])
    return data["data"]


# * Method to simplify readability of flow
# * Calls the methods that check if the solution contains all of the white listed words and non of the black listed words
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
    # * returns the syntax violations
    result_dict["violations"] = check_spelling(sol_wo_strings_and_comments, challengeData["lang"])
    return result_dict


# * Check if the sanitized solution(without comments and strings) contains all of the words in the white-listed words array
# * Return a custom feedback message and a boolean indicating if words were missing
def solution_contains_approved_words(sanitized_solution: str, challengeData):
    missing_words_set = {}
    feedback_msg = ""
    if "white_list" in challengeData:
        missing_words_set = (
            {
                word
                for word in challengeData["white_list"]
                if word not in sanitized_solution
            }
            if "white_list" in challengeData
               and type(challengeData["white_list"]) is list
            else check_keyword_loopx_challeneges(
                sanitized_solution, challengeData["white_list"]
            )
        )
        feedback_msg = (
            "Your code is missing some required-elements, like: {0}".format(
                ", ".join(missing_words_set)
            )
            if missing_words_set
            else "Code contains all required elements"
        )
    return (
        feedback_msg,
        not bool(missing_words_set),
    )


def check_spelling(sanitized_code, lang):
    # * sends the correct pattern depending on language
    results = lang_spell_check(sanitized_code, correct_patterns[lang] if lang in correct_patterns else [])
    return results


def lang_spell_check(code, patterns):
    violations = {"violations" : []}
    correct_lang_patterns = patterns
    # * checks if any of the values in the correct_patterns are present in the code
    for i, item in enumerate(correct_lang_patterns):
        matches = re.finditer(item, code, re.IGNORECASE)
        for m in matches:
            word = code[m.start():m.end()]
            if word != correct_lang_patterns[i]:
                index = code.find(word)
                # * returns the code before the error
                substring = code[:index]
                # * counts the number of lines before the error
                line_num = substring.count('\n')
                violations["violations"].append(
                    {
                        "line": line_num+1,
                        "column": 0,
                        "id": "'{0}' should be '{1}'".format(word, correct_lang_patterns[i]),
                    })
    # * if there are violations, the exitCode should be 2
    if len(violations["violations"]) > 0:
        violations["exitCode"] = 2
    return violations


# * A method to check for keywords in challenges migrated from older platform
# * A string of key words might look something like this: "for:while;if;next"
# * Words that have ":" between them is equal to "or", so one of them is needed to appear
# * ";" is equal to "and" which means all of those should exist within the solution
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
    illegal_words_set = (
        {word for word in challengeData["black_list"] if word in sanitized_solution}
        if "black_list" in challengeData
        else {}
    )
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
    # * For Java "Class" exercises specifically, we need to edit the solution slightly
    solution = (
        edit_java_class_solution(solution)
        if challengeData["lang"] == "java" and solution.strip().startswith("class")
        else solution
    )
    solution_with_tests = (
        challengeData["boiler"] if "boiler" in challengeData else solution
    )
    if "is_main" in challengeData and not challengeData["is_main"]:
        solution_with_tests = (
            solution_with_tests.replace("{{tests}}", challengeData["tests"] or "")
            if "tests" in challengeData
            else solution
        )
    elif "is_main" in challengeData and challengeData["is_main"]:
        solution_with_tests = solution_with_tests.replace("{{tests}}", solution)
        solution_with_tests = solution_with_tests.replace("{{code}}", "")

    solution_with_tests = solution_with_tests.replace("{{code}}", solution)
    solution_with_tests = (
        solution_with_tests.replace("{{classes}}", challengeData["classes"] or "")
        if "classes" in challengeData
        else solution
    )
    return solution_with_tests


# * To run and call inner classes in Java within the main method they have to be static
# * We add it here to prevent confusing the user when solving the challenge
def edit_java_class_solution(solution: str):
    return "static " + solution


# * Sending a POST request to the "free-coding-orchestrator" which runs the compiler and analyzer
def calling_free_code_orchestrator(code: str, lang: str, lint: bool, input: str):
    # * Creating the body of the request with programming-language(lang), code-to-compile(code), and run-linter(lint)
    # * lint = False, means to not run the Code-Analyzer
    body = {"lang": lang, "code": code, "lint": lint, "input": input}
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


def saving_user_challenge_data(data: ChallengeData, userId: str, solved: bool):
    # * Creating the body of the request with, was the answer right(solved), the code user submitted (lastCode)
    body = {
        "solved": solved,
        "lastCode": data.code,
        "userId": userId,
        "toSubmit": data.toSubmit,
        "time_spent": data.time_spent,
        "challenge_title": data.title,
    }
    courseID = data.courseId
    challengeID = data.challengeId
    # * json.dumps() converts the dictionary(body), to a valid JSON, for example turning "False" to "false"
    DATA = json.dumps(body)
    data = {}
    # * Setting the URL of the put request to the courses service, which stores the data of the challenge
    URL = settings.courses_service_url + "/update/" + courseID + "/" + challengeID
    try:
        result = requests.put(url=URL, data=DATA)
        data = result.json()
    except:
        # * Throwing an error if the courses service failed and returned an error
        raise SystemExit(sys.exc_info()[0])
    return data
