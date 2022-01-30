##########################
## Milestone 2 : CS335A ##
#######################################
## Submission Date: February 1, 2022 ##
########################################################################################
## lexer.py: a scanner for the source language to output the tokens in a tabular form ##
########################################################################################

__author__ = "Group 26, CS335A"


import argparse
import ply.lex as lex


def columnno(input, token):
    line_start = input.rfind("\n", 0, token.lexpos) + 1
    return (token.lexpos - line_start) + 1


lexer = lex.lex()
lex.colno = 0

tokens = (
    #Operators and Punctuation
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
)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A scanner for the source language to output the tokens in a tabular form"
    )
    parser.add_argument("filepath", type=str, help="Path for your go program")
    args = parser.parse_args()

    with open(args.filepath) as f:
        program = f.read()

    lexer.input(program)

    formatter = "{:<15} {:<15} {:<15} {:<15}"
    print(formatter.format("Token", "Lexeme", "Line#", "Column#"))

    # Our tab '\t' uses 1 column
    while True:
        tok = lexer.token()
        if not tok:
            break
        print(formatter.format(tok.type, tok.value, tok.lineno, columnno(program, tok)))
