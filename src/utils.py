#################
## Milestone 3  : CS335A ##
########################################
## Submission Date : February 18, 2022 ##
########################################

__author__ = "Group 26, CS335A"
__filename__ = "utils.py"
__description__ = "Helper/Utility functions for compiler."


SYMBOL_TABLE_DUMP_FILENAME = "symtab.csv"
AST_FILENAME = "ast.dot"
AST_PLOT_FILENAME = "ast_plot.png"

TOKENS_TO_IGNORE = ["{", "}", "(", ")", ";", "[", "]", ","]


class Format:
    """
    Collection of ANSI escape sequences to format strings
    """
    success = "\033[32m"
    fail = "\033[91m"
    end = "\033[0m"
    underline = "\033[4m"


class Node:
    def __init__(
        self,
        name="",
        val="",
        line_num=0,
        type="",
        children=[],
        array=[],
        func=0,
        level=0,
        ast=None,
    ):
        self.name = name
        self.val = val
        self.type = type
        self.line_num = line_num
        self.array = array
        self.func = func
        self.ast = ast
        self.level = level
        if children:
            self.children = children
        else:
            self.children = []


def ignore_lexer_literal(s):
    if s in TOKENS_TO_IGNORE:
        return True
    return False


def write_label(filename: str, a: str, b: str):
    with open(filename, "a") as f:
        f.write("\n" + a + '[label="' + b + '"]')


def write_edge(filename: str, a: str, b: str):
    with open(filename, "a") as f:
        f.write("\n" + a + " -> " + b)
