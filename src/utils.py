###########################
## Milestone 5 : CS335A ##
######################################
## Submission Date : April 10, 2022 ##
######################################

__author__ = "Group 26, CS335A"
__filename__ = "utils.py"
__description__ = "Helper/Utility functions for compiler."


import sys

from constants import TOKENS_TO_IGNORE
from classes import Format


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


def print_compilation_error(err: str):
    print(Format.fail + err + Format.end)
    sys.exit()


def print_success(err: str):
    print(Format.success + err + Format.end)


def print_failure(err: str):
    print(Format.fail + err + Format.end)


def operate(op1, op, op2):
    # Alternate :
    # return eval(f"{op1} {op} {op2}")
    if op[0] == "+":
        return op1 + op2
    if op[0] == "-":
        return op1 - op2
    if op[0] == "*":
        return op1 * op2
    if op[0] == "|":
        return op1 | op2
    if op[0] == "^":
        return op1 ^ op2
    if op[0] == "&":
        return op1 & op2
    if op == "==":
        return op1 == op2
    if op == "!=":
        return op1 != op2
    if op == ">=":
        return op1 >= op2
    if op == "<=":
        return op1 <= op2
    if op == "<":
        return op1 < op2
    if op == ">":
        return op1 > op2


def get_dim(type):
    temp = type.split()
    i = 0
    dim = []
    while temp[i] == "ARRAY":
        i = i + 1
        dim.append(int(temp[i]))
        i = i + 1
    return dim


def convertible(s1, s2):
    if s1 == s2:
        return True
    else:
        if isint(s2):
            if isint(s1):
                return True
            else:
                return False
        else:
            if s2 == "FLOAT32" or s2 == "FLOAT64":
                if s1 in ["FLOAT32", "FLOAT64", "floatconst"] or isint(s1):
                    return True
                else:
                    return False


def isint(s):
    if s in [
        "stringconst",
        "boolconst",
        "BOOL",
        "STRING",
        "floatconst",
        "FLOAT32",
        "FLOAT64",
    ]:
        return False
    else:
        return True


def notcomparable(s):
    if s in ["stringconst", "boolconst", "BOOL", "STRING"]:
        return True
    else:
        return False


def equal(s1, s2):
    if s1 == s2:
        return s1
    else:
        if not (
            s1 in ["intconst", "floatconst", "stringconst", "boolconst"]
            or s2 in ["intconst", "floatconst", "stringconst", "boolconst"]
        ):
            return ""

        if s1 in ["intconst", "floatconst", "stringconst", "boolconst"]:
            if isint(s2) and s1 == "intconst":
                return s2
            elif s2 in ["FLOAT32", "FLOAT64"] and s1 == "floatconst":
                return s2
            elif s2 == "BOOL" and s1 == "boolconst":
                return s2
            elif s2 == "STRING" and s1 == "stringconst":
                return s2
        else:
            return equal(s2, s1)

    return ""


def write_ircode(filename: str, ircode):
    with open(filename, "w") as f:
        for line in ircode:
            for word in line:
                f.write(str(word) + " ")
            f.write("\n")


def get_store_instruction(s):
    if s == "INT":
        return "sw"
    elif s == "INT8":
        return "sb"
    elif s == "INT16":
        return "sh"
    elif s == "INT32":
        return "sw"
    elif s == "INT64":
        return "sw"
    elif s == "UINT":
        return "sw"
    elif s == "UINT8":
        return "sb"
    elif s == "UINT16":
        return "sh"
    elif s == "UINT32":
        return "sw"
    elif s == "UINT64":
        return "sw"


def equalarray(p, q):
    temp1 = p.split()
    temp2 = q.split()
    if len(temp1) != len(temp2):
        return False
    for i in range(len(temp1) - 1):
        if temp1[i] != temp2[i]:
            return False
    if equal(temp1[-1], temp2[-1]) == "":
        return False
    return True


def getsize(a):
    pass
