##########################
## Milestone 2 : CS335A ##
#######################################
## Submission Date: February 1, 2022 ##
#######################################

__author__ = "Group 26, CS335A"
__filename__ = "lexer.py"
__description__ = (
    "A scanner for the source language to output the tokens in a tabular form"
)

import argparse
import ply.lex as lex
from ply.lex import TOKEN


class Format:
    """
    Collection of ANSI escape sequences to format strings
    """

    fail = "\033[91m"
    end = "\033[0m"
    underline = "\033[4m"


prev = 0

KEYWORDS = [
    "break",
    "default",
    "func",
    "case",
    "struct",
    "else",
    "package",
    "switch",
    "const",
    "if",
    "range",
    "type",
    "continue",
    "for",
    "import",
    "return",
    "var",
]

SPECIAL_WORDS = [
    "int8",
    "int16",
    "int32",
    "int64",
    "int",
    "float32",
    "float64",
    "uint8",
    "uint16",
    "uint32",
    "uint64",
    "bool",
    "string",
]

RESERVED = KEYWORDS + SPECIAL_WORDS

OPERATORS_AND_PUNCTUATIONS = [
    "RIGHT_SHIFT_EQUAL",
    "LEFT_SHIFT_EQUAL",
    "RIGHT_SHIFT",
    "LEFT_SHIFT",
    "PLUS_ASSIGN",
    "MINUS_ASSIGN",
    "MULT_ASSIGN",
    "DIV_ASSIGN",
    "MOD_ASSIGN",
    "AND_ASSIGN",
    "OR_ASSIGN",
    "XOR_ASSIGN",
    "COLON_ASSIGN",
    "AND",
    "OR",
    "INCREMENT",
    "DECREMENT",
    "EQUAL",
    "NOT_EQUAL",
    "LESS_EQUAL",
    "GREATER_EQUAL",
    "PLUS",
    "MINUS",
    "MULT",
    "DIV",
    "MOD",
    "BIT_AND",
    "BIT_OR",
    "BIT_XOR",
    "LESS",
    "GREATER",
    "ASSIGN",
    "NOT",
    "LEFT_PARENTH",
    "RIGHT_PARENTH",
    "LEFT_SQUARE",
    "RIGHT_SQUARE",
    "LEFT_BRACE",
    "RIGHT_BRACE",
    "COMMA",
    "DOT",
    "COLON",
    "SEMICOLON",
]

tokens = (
    OPERATORS_AND_PUNCTUATIONS
    + [
        "IDENTIFIER",
        "FLOATCONST",
        "INTCONST",
        "BOOLCONST",
        "STRINGCONST",
        "COMMENT",
        "NEWLINE",
    ]
    + [word.upper() for word in RESERVED]
)

characters_to_ignore = [" ", "\t"]

t_RIGHT_SHIFT_EQUAL = r">>="
t_LEFT_SHIFT_EQUAL = r"<<="
t_RIGHT_SHIFT = r">>"
t_LEFT_SHIFT = r"<<"
t_PLUS_ASSIGN = r"\+="
t_MINUS_ASSIGN = r"-="
t_MULT_ASSIGN = r"\*="
t_DIV_ASSIGN = r"/="
t_MOD_ASSIGN = r"%="
t_AND_ASSIGN = r"&="
t_OR_ASSIGN = r"\|="
t_XOR_ASSIGN = r"\^="
t_COLON_ASSIGN = r":="
t_AND = r"&&"
t_OR = r"\|\|"
t_INCREMENT = r"\+\+"
t_DECREMENT = r"--"
t_EQUAL = r"=="
t_NOT_EQUAL = r"!="
t_LESS_EQUAL = r"<="
t_GREATER_EQUAL = r">="
t_PLUS = r"\+"
t_MINUS = r"-"
t_MULT = r"\*"
t_DIV = r"/"
t_MOD = r"%"
t_BIT_AND = r"&"
t_BIT_OR = r"\|"
t_BIT_XOR = r"\^"
t_LESS = r"<"
t_GREATER = r">"
t_ASSIGN = r"="
t_NOT = "!"
t_LEFT_PARENTH = r"\("
t_RIGHT_PARENTH = r"\)"
t_LEFT_SQUARE = r"\["
t_RIGHT_SQUARE = r"\]"
t_LEFT_BRACE = r"\{"
t_RIGHT_BRACE = r"\}"
t_COMMA = r","
t_DOT = r"\."
t_COLON = r":"
t_SEMICOLON = r";"


## Making regex for integer literals
decimal_literal = r"[1-9][0-9]*"
octal_literal = r"(0|0o|0O)[0-7]*"
hex_literal = r"0[xX][a-fA-F0-9]+"
int_literal = r"(" + decimal_literal + r"|" + hex_literal + r"|" + octal_literal + r")"

## Making regex for float literals
number = r"(0|[1-9][0-9]*)"
decimal = r"[0-9]+"
exp = r"(e|E)[\+-]?" + decimal
float_type1 = number + exp
float_type2 = r"(" + number + r")\.(" + decimal + r")?(" + exp + r")?"
float_type3 = r"\." + decimal + r"(" + exp + r")?"
float_literal = r"(" + float_type1 + r"|" + float_type2 + r"|" + float_type3 + r")"


bool_literal = r"true|false"

## Making regex for comment
comment_type1 = r"//.*"  # Single line comment
comment_type2_1 = r"(\*[^\/])"  # Multiline with *
comment_type2_2 = r"[^*]"  # Multiline without *
comment_regex = (
    r"("
    + comment_type1
    + r"|"
    + r"\/\*("
    + comment_type2_1
    + r"|"
    + comment_type2_2
    + r")*\*\/)"
)

## Making regex for string literals
string_type1 = r"\\[^\n]"  # contains backslash
string_type2 = r"[^\"\\\n]"  # doesn't contain backslash , "*", newline
string_regex = r"(" + r"\"(" + string_type1 + r"|" + string_type2 + r")*\")"


@TOKEN(bool_literal)
def t_BOOLCONST(t):
    """
    Check for boolean constants
    It is kept above t_IDENTIFIER function to avoid true and false being classfied as IDENTIFIER
    """
    return t


# Checks for reserved words and identifier
def t_IDENTIFIER(t):
    r"[a-zA-Z_][a-zA-Z0-9_]*"
    if t.value in RESERVED:
        t.type = t.value.upper()
    return t


@TOKEN(float_literal)
def t_FLOATCONST(t):
    """
    Check for float constants like 2e5, .35, 10.10 using float_literal regex
    It is placed above t_INTCONST to avoid, for example,
    misclassifying 12.12, which is FLOATCONST as INTCONST followed by DOT followed by INTCONST
    """
    return t


@TOKEN(int_literal)
def t_INTCONST(t):
    """
    Check for integer constants like 2, 0x4, 0o25
    """
    return t


@TOKEN(comment_regex)
def t_COMMENT(t):
    ## Updates line no. and prev global variable
    spl = t.value.split("\n")
    curr_len = len(t.value)
    end = t.lexpos + curr_len - 1
    global prev
    prev = end - len(spl[len(spl) - 1])
    t.lexer.lineno += len(spl) - 1
    pass


@TOKEN(string_regex)
def t_STRINGCONST(t):
    """
    Note that Go does not support multiline strings,
    and we intend it keep it the same.
    """
    return t


def t_NEWLINE(t):
    r"\n+"
    ## Updates line no. and prev global variable
    curr_len = len(t.value)
    t.lexer.lineno += curr_len
    global prev
    prev = t.lexpos + curr_len - 1
    pass


def t_error(t):
    """
    Custom error function for lexer.

    Nicely formats the error message in red color
    """
    error = "> Illegal character '{}', at line#{} and column#{}"
    try:
        print(
            Format.fail
            + error.format(t.value[0], t.lexer.lineno, columnno(t))
            + Format.end
        )
    except:
        print(error.format(t.value[0], t.lexer.lineno, columnno(t)))
    t.lexer.skip(1)


def columnno(t):
    """
    Custom utility to find column no of each lexeme.

    Global variable `prev` stores the index position of last lexeme (which is '\n') on line
    previous to that of given lexeme. Hence, t.lexpos - prev outputs the desired column no.
    """
    global prev
    return t.lexpos - prev


t_ignore = "".join(characters_to_ignore)

lexer = lex.lex()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A scanner for the source language to output the tokens in a tabular form"
    )
    parser.add_argument("filepath", type=str, help="Path for your go program")
    args = parser.parse_args()

    with open(args.filepath) as f:
        program = f.read()

    lexer.input(program)

    header_formatter = Format.underline + "{:<20} {:<20} {:<10} {:<10}" + Format.end
    formatter = "{:<20} {:<20} {:<10} {:<10}"
    header = ["Token", "Lexeme", "Line#", "Column#"]
    try:
        print(header_formatter.format(*header))
    except:
        print(formatter.format(*header))

    ## Note: Our tab '\t' uses 1 column
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(formatter.format(tok.type, tok.value, tok.lineno, columnno(tok)))
