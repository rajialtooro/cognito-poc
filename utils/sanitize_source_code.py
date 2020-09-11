import sys, token, os, re
import tokenize
from io import BytesIO


def sanitize_source_code(code: str, lang: str) -> str:
    code_without_comments = getattr(sys.modules[__name__], "clean_comments_%s" % lang)(
        code
    )
    return remove_strings(code_without_comments)


def clean_comments(code: str, lang: str):
    return getattr(sys.modules[__name__], "clean_comments_%s" % lang)(code)


"""
Source of method: https://stackoverflow.com/a/2962727
"""


def clean_comments_python(source):
    """
    Returns 'source' minus comments and docstrings.
    """
    io_obj = source
    out = ""
    prev_toktype = tokenize.INDENT
    last_lineno = -1
    last_col = 0
    for tok in tokenize.tokenize(BytesIO(io_obj.encode("utf-8")).readline):
        token_type = tok[0]
        token_string = tok[1]
        start_line, start_col = tok[2]
        end_line, end_col = tok[3]
        ltext = tok[4]
        # The following two conditionals preserve indentation.
        # This is necessary because we're not using tokenize.untokenize()
        # (because it spits out code with copious amounts of oddly-placed
        # whitespace).
        if start_line > last_lineno:
            last_col = 0
        if start_col > last_col:
            out += " " * (start_col - last_col)
        # Remove comments:
        if token_type == tokenize.COMMENT:
            pass
        # This series of conditionals removes docstrings:
        elif token_type == tokenize.STRING:
            if prev_toktype != tokenize.INDENT:
                # This is likely a docstring; double-check we're not inside an operator:
                if prev_toktype != tokenize.NEWLINE:
                    # Note regarding NEWLINE vs NL: The tokenize module
                    # differentiates between newlines that start a new statement
                    # and newlines inside of operators such as parens, brackes,
                    # and curly braces.  Newlines inside of operators are
                    # NEWLINE and newlines that start new code are NL.
                    # Catch whole-module docstrings:
                    if start_col > 0:
                        # Unlabelled indentation means we're inside an operator
                        out += token_string
                    # Note regarding the INDENT token: The tokenize module does
                    # not label indentation inside of an operator (parens,
                    # brackets, and curly braces) as actual indentation.
                    # For example:
                    # def foo():
                    #     "The spaces before this docstring are tokenize.INDENT"
                    #     test = [
                    #         "The spaces before this string do not get a token"
                    #     ]
        else:
            out += token_string
        prev_toktype = token_type
        last_col = end_col
        last_lineno = end_line
    lst = out.split("\n")
    del lst[0]
    return "\n".join(lst)


def remove_strings(source):
    clean_code = re.sub(r'"(.*?)"', "", source)
    clean_code = re.sub(r"'(.*?)'", "", clean_code)
    clean_code = re.sub(r"`(.*?)`", "", clean_code)
    return clean_code


def clean_comments_java(source):
    clean_code = re.sub(r"\/\*[\s\S]*?\*\/|\/\/.*", "", source)
    return clean_code


def clean_comments_c(source):
    return clean_comments_java(source)


def clean_comments_cs(source):
    return clean_comments_java(source)


def clean_comments_javascript(source):
    return source


def escape_reg_exp(expression):
    return re.sub("/[.*+?^${}()|[\]\\]/g", "\\$&", expression)
