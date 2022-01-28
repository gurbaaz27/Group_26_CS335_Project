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
