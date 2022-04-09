#################
## Milestone 3  : CS335A ##
########################################
## Submission Date : February 18, 2022 ##
########################################

__author__ = "Group 26, CS335A"
__filename__ = "parser.py"
__description__ = "A parser for the source language that outputs the Parser Automaton in a graphical form."

import sys
import argparse
from pprint import pprint
import ply.yacc as yacc
from lexer import tokens
from utils import (
    SYMBOL_TABLE_DUMP_FILENAME,
    AST_FILENAME,
    AST_PLOT_FILENAME,
    write_label,
    write_edge,
    ignore_lexer_literal,
    print_compilation_error,
    print_success,
    print_failure,
    Node,
    Format,
)
import pydot
import copy
import json

######################
## Global Variables ##
######################

SYMBOL_TABLE = []
SYMBOL_TABLE.append({})

_current_function_return_type = ""
_current_function_name = ""

_current_scope = 0
_next_scope = 1

_parent = {}
_parent[0] = 0

_loop_depth = 0
_switch_depth = 0

_current_number = 0

size = {}
size["int"] = 4
size["char"] = 1
size["float"] = 4


start_node = Node("START", val="", type="", children=[])

precedence = (
    ("left", "COMMA"),
    (
        "right",
        "ASSIGN",
        "PLUS_ASSIGN",
        "MINUS_ASSIGN",
        "STAR_ASSIGN",
        "DIV_ASSIGN",
        "MOD_ASSIGN",
        "AND_ASSIGN",
        "OR_ASSIGN",
        "XOR_ASSIGN",
        "COLON_ASSIGN",
        "RIGHT_SHIFT_EQUAL",
        "LEFT_SHIFT_EQUAL",
    ),
    ("left", "OR"),
    ("left", "AND"),
    ("left", "BIT_OR"),
    ("left", "BIT_XOR"),
    ("left", "BIT_AND"),
    ("left", "EQUAL", "NOT_EQUAL"),
    ("left", "LESS_EQUAL", "GREATER_EQUAL", "LESS", "GREATER"),
    ("left", "RIGHT_SHIFT", "LEFT_SHIFT"),
    ("left", "PLUS", "MINUS"),
    ("left", "STAR", "DIV", "MOD"),
    (
        "left",
        "RIGHT_PARENTH",
        "LEFT_PARENTH",
        "LEFT_BRACE",
        "RIGHT_BRACE",
        "LEFT_SQUARE",
        "RIGHT_SQUARE",
        "INCREMENT",
        "DECREMENT",
    ),
)


def add_edges(p, exclude=[]):
    global _current_number
    global child_num
    global child_val

    stripped_p_ = sys._getframe(1).f_code.co_name[2:]
    length = len(p)

    if length != 2:
        _current_number += 1
        p_count = _current_number
        i = 1

        write_label(AST_FILENAME, str(p_count), stripped_p_.replace('"', ""))

        for child in range(1, length, 1):
            if i in exclude:
                i += 1
                continue
            i += 1
            if type(p[child]) is Node and p[child].ast is None:
                continue

            if type(p[child]) is not Node:
                if type(p[child]) is tuple:
                    if ignore_lexer_literal(p[child][0]) is False:
                        write_edge(AST_FILENAME, str(p_count), str(p[child][1]))
                else:
                    if ignore_lexer_literal(p[child]) is False:
                        _current_number += 1
                        write_label(
                            AST_FILENAME,
                            str(_current_number),
                            str(p[child]).replace('"', ""),
                        )
                        p[child] = (p[child], _current_number)
                        write_edge(AST_FILENAME, str(p_count), str(p[child][1]))
            else:
                if type(p[child].ast) is tuple:
                    if ignore_lexer_literal(p[child].ast[0]) is False:
                        write_edge(AST_FILENAME, str(p_count), str(p[child].ast[1]))
                else:
                    if ignore_lexer_literal(p[child].ast) is False:
                        _current_number += 1
                        write_label(
                            AST_FILENAME,
                            str(_current_number),
                            str(p[child].ast).replace('"', ""),
                        )
                        p[child].ast = (p[child].ast, _current_number)
                        write_edge(AST_FILENAME, str(p_count), str(p[child].ast[1]))

        return stripped_p_, p_count

    else:
        if type(p[1]) is Node:
            return p[1].ast
        else:
            return p[1]


def find_if_ID_is_declared(id, lineno):
    curscp = _current_scope
    while _parent[curscp] != curscp:
        if id in SYMBOL_TABLE[curscp].keys():
            return curscp
        curscp = _parent[curscp]
    if curscp == 0:
        if id in SYMBOL_TABLE[curscp].keys():
            return curscp
    print_compilation_error(
        lineno, "COMPILATION ERROR: unary_expression " + id + " not declared"
    )

    return -1


def find_scope(id, lineno):
    curscp = _current_scope
    while _parent[curscp] != curscp:
        if id in SYMBOL_TABLE[curscp].keys():
            return curscp
        curscp = _parent[curscp]
    if curscp == 0:
        if id in SYMBOL_TABLE[curscp].keys():
            return curscp
    return -1


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


def p_start(p):
    """start : SourceFile"""
    p[0] = p[1]


def p_empty(p):
    """empty :"""
    # p[0] = Node(name="Empty", val="", children=[], type="")
    # p[0].ast = add_edges(p)


###############
##### EOS #####
###############


def p_EOS(p):
    """EOS : SEMICOLON"""
    p[0] = p[1]


#################
##### TYPE #####
#################


def p_TypeName_1(p):
    """TypeName : UINT
    | UINT8
    | UINT16
    | UINT32
    | UINT64
    | INT
    | INT8
    | INT16
    | INT32
    | INT64
    | FLOAT32
    | FLOAT64
    | BOOL
    | STRING
    """
    p[0] = Node(
        name="TypeName", val="", type=p[1].upper(), line_num=p.lineno(1), children=[]
    )
    p[0].ast = add_edges(p)


def p_TypeName_2(p):
    """TypeName : IDENTIFIER"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]
    p[0] = Node(
        name="TypeName",
        val="",
        type="struct " + lexeme,
        line_num=p.lineno(1),
        children=[],
    )
    p[0].ast = add_edges(p)


def p_TypeLit(p):
    """TypeLit : StructType
    | ArrayType
    | SliceType
    | PointerType
    """
    p[0] = Node(
        name="TypeLit", val="", type=p[1].type, line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)


def p_Type(p):
    """Type : TypeName
    | TypeLit
    | LEFT_PARENTH Type RIGHT_PARENTH
    """
    if len(p) == 2:
        p[0] = Node(
            name="Type", val="", type=p[1].type, line_num=p[1].line_num, children=[]
        )
        p[0].ast = add_edges(p)

    else:
        p[0] = Node(
            name="Type", val="", type=p[2].type, line_num=p.lineno(1), children=[]
        )
        p[0].ast = add_edges(p)


#################
##### ARRAY #####
#################


def p_ArrayType(p):
    """ArrayType : LEFT_SQUARE ArrayLength RIGHT_SQUARE ElementType"""

    p[0] = Node(
        name="ArrayType",
        val="",
        type="ARRAY " + str(p[2].val) + " " + p[4].type,
        line_num=p.lineno(1),
        children=[],
    )
    p[0].ast = add_edges(p)


def p_ArrayLength(p):
    """ArrayLength : Expression"""

    p[0] = Node(
        name="ArrayLength",
        val=p[1].val,
        type=p[1].type,
        line_num=p[1].line_num,
        children=[],
    )
    if p[0].type != "intconst":
        print_compilation_error(
            "Compilation Error: Array index at line ",
            p.lineno(1),
            " is not of compatible type",
        )

    p[0].ast = add_edges(p)


def p_ElementType(p):
    """ElementType : Type"""
    p[0] = Node(
        name="ElementType", val="", type=p[1].type, line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)


#################
##### SLICE #####
#################


def p_SliceType(p):
    """SliceType : LEFT_SQUARE RIGHT_SQUARE ElementType"""

    p[0] = Node(
        name="SliceType",
        val="",
        type="SLICE " + p[3].type,
        line_num=p.lineno(1),
        children=[],
    )
    p[0].ast = add_edges(p)


##################
##### STRUCT #####
##################


def p_StructType(p):
    """StructType : STRUCT LEFT_BRACE Fields RIGHT_BRACE"""

    p[0] = Node(
        name="StructType",
        val="",
        type="STRUCT " + str(p[3].numFields) + " " + p[3].type,
        line_num=p.lineno(1),
        children=[],
    )
    p[0].ast = add_edges(p)


def p_Fields(p):
    """Fields : FieldDecl EOS Fields
    | empty"""

    if len(p) == 2:
        p[0] = Node(name="Fields", val="", type="", line_num=p.lineno(1), children=[])
        p[0].numFields = 0
        p[0].ast = add_edges(p, [1])
    else:
        p[0] = Node(
            name="Fields",
            val="",
            type=p[1].type + " " + p[3].type,
            line_num=p.lineno(1),
            children=[],
        )
        p[0].numFields = p[3].numFields + 1
        p[0].ast = add_edges(p)


def p_FieldDecl(p):
    """FieldDecl : IDENTIFIER Type"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]
    p[0] = Node(
        name="FieldDecl",
        val="",
        type=lexeme + " " + p[2].type,
        line_num=p.lineno(1),
        children=[],
    )
    p[0].ast = add_edges(p)


#############
## POINTER ##
#############
def p_PointerType(p):
    """PointerType : STAR Type"""
    p[0] = Node(
        name="PointerType",
        val="",
        type=p[2].type + "*",
        line_num=p.lineno(1),
        children=[],
    )
    p[0].ast = add_edges(p)


###########
## BLOCK ##
###########
def p_LopenBrace(p):
    """LopenBrace : LEFT_BRACE"""
    global _current_scope
    global _next_scope

    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1

    p[0] = p[1]
    p[0] = add_edges(p)


def p_Block(p):
    """Block : LopenBrace StatementList RIGHT_BRACE"""
    global _current_scope
    _current_scope = _parent[_current_scope]

    p[0] = Node(name="Block", val="", line_num=p.lineno(1), type="", children=[])
    p[0].ast = add_edges(p)


def p_StatementList(p):
    """StatementList : Statement EOS StatementList
    | empty"""
    if len(p) == 2:
        p[0] = p[1]
        p[0] = add_edges(p)
    else:
        p[0] = Node(
            name="StatementList", val="", type="", children=[], line_num=p[1].line_num
        )

        if type(p[3]) is Node:
            p[0].ast = add_edges(p, [2])
            if p[3].name != "StatementList":
                p[0].children.append(p[3])
            else:
                p[0].children = p[3].children

            p[0].children.append(p[1])

        else:
            p[0].ast = add_edges(p, [2, 3])


###############
## STATEMENT ##
###############
def p_Statement(p):
    """Statement : Declaration
    | SimpleStmt
    | ReturnStmt
    | BreakStmt
    | Block
    | ContinueStmt
    | IfStmt
    | SwitchStmt
    | ForStmt"""
    p[0] = Node(name="Statement", val="", type="", children=[], line_num=p[1].line_num)
    p[0].ast = add_edges(p)


## RETURN STATEMENT
def p_ReturnStmt(p):
    """ReturnStmt : RETURN Expression
    | RETURN"""
    if len(p) == 2:
        p[0] = Node(
            name="ReturnStmt", val="", type="", children=[], line_num=p.lineno(1)
        )
        p[0].ast = add_edges(p)

        if _current_function_return_type != "void":
            print_compilation_error(
                "COMPILATION ERROR at line "
                + str(p.lineno(1))
                + ": function return type is not void"
            )

    else:

        if p[2].type != "" and _current_function_return_type != p[2].type:
            print_compilation_error(
                "COMPLIATION ERROR at line "
                + str(p.lineno(1))
                + ": function return type is not "
                + p[2].type
            )

        p[0] = Node(
            name="ReturnStmt", val="", type="", line_num=p.lineno(1), children=[]
        )
        p[0].ast = add_edges(p, [2])


## BREAK STATEMENT
def p_BreakStmt(p):
    """BreakStmt : BREAK Expression
    | BREAK"""
    global _loop_depth
    global _switch_depth
    p[0] = Node(name="BreakStmt", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)
    if p[2].type != "intconst":
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[0].line_num)
            + "argument to  break should be a constant"
        )

    if _loop_depth == 0 or _switch_depth == 0:
        print_compilation_error(p[0].line_num, ": break not inside loop")


## CONTINUE STATEMENT
def p_ContinueStmt(p):
    """ContinueStmt : CONTINUE"""
    global _loop_depth
    p[0] = Node(name="ContinueStmt", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)

    if _loop_depth == 0:
        print_compilation_error(p[0].line_num, ": continue not inside loop")


## DECLARATION
def p_Declaration(p):  # pending
    """Declaration : ConstDecl
    | TypeDecl
    | VarDecl"""
    p[0] = Node(
        name="Declaration", val="", type="", line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)


def p_TopLevelDecl(p):  # pending
    """TopLevelDecl : Declaration
    | FunctionDecl"""
    p[0] = Node(
        name="TopLevelDecl", val="", type="", line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)


def p_TopLevelDeclList_1(p):  # pending
    """TopLevelDeclList : TopLevelDecl EOS TopLevelDeclList
    | TopLevelDecl"""
    p[0] = Node(
        name="TopLevelDeclList", val="", type="", line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)


def p_TopLevelDeclList_2(p):  # pending
    """TopLevelDeclList : empty"""
    p[0] = Node(name="TopLevelDeclList", val="", type="", children=[])
    p[0].ast = add_edges(p)


def p_SourceFile(p):  # pending
    """SourceFile : TopLevelDeclList"""
    p[0] = Node(name="SourceFile", val="", type="", line_num=p[1].line_num, children=[])
    p[0].ast = add_edges(p)


## 1. ConstDecl
def p_ConstDecl(p):  # pending
    """ConstDecl : CONST ConstSpec"""
    p[0] = Node(name="ConstDecl", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


def p_ConstSpec(p):
    """ConstSpec : IDENTIFIER Type ASSIGN Expression
    | IDENTIFIER ASSIGN Expression"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]
    if lexeme in SYMBOL_TABLE[_current_scope].keys():
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p.lineno(1))
            + " : "
            + lexeme
            + " already declared "
        )

    if len(p) == 5:
        if p[2].type != p[4].type:

            if p[4].type not in ["intconst", "floatconst", "stringconst", "boolconst"]:

                ##TODO: correct 2.go
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif (
                p[2].type
                in [
                    "INT",
                    "INT8",
                    "INT16",
                    "INT32",
                    "INT64",
                    "UINT",
                    "UINT8",
                    "UINT16",
                    "UINT32",
                    "UINT64",
                ]
                and p[4].type != "intconst"
            ):
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif p[2].type in ["FLOAT32", "FLOAT64"] and not (
                p[4].type == "intconst" or p[4].type == "floatconst"
            ):
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )
            elif p[2].type == "STRING" and p[4].type != "stringconst":
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif p[2].type == "BOOL" and p[4].type != "boolconst":
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif p[2].type.startswith("ARRAY"):
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

        if not p[2].type.startswith("ARRAY"):
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1
        else:
            # Pass complete array string
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
            i = 0
            temp = p[3].type.split()
            dim = []
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                i = i + 1
            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1

    elif len(p) == 4:
        if p[3].type == "intconst":
            p[3].type = "INT64"
        elif p[3].type == "floatconst":
            p[3].type = "FLOAT64"
        elif p[3].type == "stringconst":
            p[3].type = "STRING"
        elif p[3].type == "boolconst":
            p[3].type = "BOOL"

        if not p[3].type.startswith("ARRAY"):
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1
        else:
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            i = 0
            temp = p[3].type.split()
            dim = []
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                i = i + 1
            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1

    else:
        if not p[2].type.startswith("ARRAY"):
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1
        else:
            # Pass complete array string
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
            i = 0
            temp = p[3].type.split()
            dim = []
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                i = i + 1
            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1

    p[0] = Node(name="ConstSpec", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


## 2. Typedecl
def p_TypeDecl(p):  # pending
    """TypeDecl : TYPE TypeSpec"""
    p[0] = Node(name="TypeDecl", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


def p_TypeSpec(p):  # pending
    """TypeSpec : AliasDecl
    | TypeDef"""
    p[0] = Node(name="TypeSpec", val="", type="", line_num=p[1].line_num, children=[])
    p[0].ast = add_edges(p)


def p_AliasDecl(p):  # pending
    """AliasDecl : IDENTIFIER ASSIGN Type"""
    p[0] = Node(name="AliasDecl", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


def p_TypeDef(p):
    """TypeDef : IDENTIFIER Type"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    # Here type must be a struct, as others are not supported
    temp = p[2].type.split()
    if temp[0] != "STRUCT":
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[2].line_num)
            + " : "
            + "Incorrect struct type specification"
        )

    sym = "struct " + lexeme
    fields = []
    i = 2

    while i < len(temp):
        curr = []
        curr.append(temp[i])
        i = i + 1
        typ = ""
        while temp[i] == "ARRAY":
            typ = typ + " ARRAY"
            i = i + 1
            # dim.append(int(temp[i]))
            typ = typ + " " + temp[i]
            i = i + 1
        if temp[i] == "struct":
            typ = typ + " struct"
            i = i + 1
        typ = typ + " " + temp[i]
        i = i + 1
        curr.append(typ.strip())
        fields.append(curr)

    SYMBOL_TABLE[_current_scope][sym] = {}
    SYMBOL_TABLE[_current_scope][sym]["field_list"] = fields
    p[0] = Node(name="TypeDef", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


## 3. VarDecl
def p_VarDecl(p):  # pending
    """VarDecl : VAR VarSpec"""
    p[0] = Node(name="VarDecl", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


## VarSpec
def p_VarSpec(p):
    """VarSpec : IDENTIFIER Type ASSIGN Expression
    | IDENTIFIER ASSIGN Expression
    | IDENTIFIER Type"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    if lexeme in SYMBOL_TABLE[_current_scope].keys():
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p.lineno(1))
            + " : "
            + lexeme
            + " already declared "
        )

    if len(p) == 5:
        if p[2].type != p[4].type:
            if p[4].type not in ["intconst", "floatconst", "stringconst", "boolconst"]:

                ##TODO: correct 2.go
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif (
                p[2].type
                in [
                    "INT",
                    "INT8",
                    "INT16",
                    "INT32",
                    "INT64",
                    "UINT",
                    "UINT8",
                    "UINT16",
                    "UINT32",
                    "UINT64",
                ]
                and p[4].type != "intconst"
            ):

                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif p[2].type in ["FLOAT32", "FLOAT64"] and not (
                p[4].type == "intconst" or p[4].type == "floatconst"
            ):
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif p[2].type == "STRING" and p[4].type != "stringconst":
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif p[2].type == "BOOL" and p[4].type != "boolconst":
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

            elif p[2].type.startswith("ARRAY"):
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p.lineno(1))
                    + " : "
                    + "Expression and specified type do not match"
                )

        if not p[2].type.startswith("ARRAY"):
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type

        else:
            # Pass complete array string
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
            i = 0
            temp = p[2].type.split()
            dim = []
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                i = i + 1
            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim

    elif len(p) == 4:
        if p[3].type == "intconst":
            p[3].type = "INT64"
        elif p[3].type == "floatconst":
            p[3].type = "FLOAT64"
        elif p[3].type == "stringconst":
            p[3].type = "STRING"
        elif p[3].type == "boolconst":
            p[3].type = "BOOL"

        if not p[3].type.startswith("ARRAY"):
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
        else:
            i = 0
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            temp = p[3].type.split()
            dim = []
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                i = i + 1
            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim

    else:
        if not p[2].type.startswith("ARRAY"):
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
        else:
            # Pass complete array string
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
            i = 0
            temp = p[2].type.split()
            dim = []
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                i = i + 1
            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim

    p[0] = Node(name="VarSpec", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


## SIMPLE STATEMENT
def p_SimpleStmt(p):
    """SimpleStmt : ExpressionStmt
    | IncDecStmt
    | Assignment
    | ShortVarDecl"""
    p[0] = Node(name="SimpleStmt", val="", type="", line_num=p[1].line_num, children=[])
    p[0].ast = add_edges(p)


def p_ExpressionStmt(p):
    """ExpressionStmt : Expression"""
    p[0] = Node(
        name="ExpressionStmt", val="", type="", line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)


# 3.
def p_IncDecStmt(p):  # to check on which all things can this be applied
    """IncDecStmt : Expression INCREMENT
    | Expression DECREMENT"""
    p[0] = Node(
        name="IncrementOrDecrementExpression",
        val=p[1].val,
        line_num=p[1].line_num,
        type=p[1].type,
        children=[],
    )
    p[0].ast = add_edges(p)
    found_scope = find_scope(
        p[1].val, p[1].line_num
    )  # this restricts the type of expressions on which it can be applied
    if found_scope == -1:
        print_compilation_error(
            "Compilation Error at line",
            str(p[1].line_num),
            ":Invalid operation on",
            p[1].val,
        )

    else:
        if (p[1].func == 1) or ("struct" in p[1].type.split()):
            print_compilation_error(
                "Compilation Error at line",
                str(p[1].line_num),
                ":Invalid operation on",
                p[1].val,
            )

        if p[1].level != 0:
            print_compilation_error(
                "Compilation Error at line",
                str(p[1].line_num),
                ":Invalid operation on",
                p[1].val,
            )


# def p_Assignment_1(p):
#     """Assignment : Expression assign_op Make_Func"""
#     pass


def p_Assignment_2(p):  # pending
    """Assignment : Expression assign_op Expression"""

    if p[1].type in ["intconst", "floatconst", "boolconst", "stringconst"]:
        print_compilation_error(
            p[1].line_num, "COMPILATION ERROR : Left hand side cannot be constant"
        )

    else:
        if p[2] == ">>=" or p[2] == "<<=":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

            else:
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].ast = add_edges(p)

        elif p[2] == "+=" or p[2] == "-=" or p[2] == "*=":
            if (
                equal(p[1].type, p[3].type) != ""
            ):  # should be exactly equal or atleast one is a constant
                if notcomparable(p[1].type):
                    print_compilation_error(
                        p[1].line_num,
                        "COMPILATION ERROR : Incomputable data type with "
                        + p[2]
                        + " operator",
                    )

                else:
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=equal(p[1].type, p[3].type),
                        children=[],
                    )
                    p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

        elif p[2] == "/=":
            if equal(p[1].type, p[3].type) != "":
                if notcomparable(p[1].type):
                    print_compilation_error(
                        p[1].line_num,
                        "COMPILATION ERROR : Incomputable data type with "
                        + p[2]
                        + " operator",
                    )

                else:
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=equal(p[1].type, p[3].type),
                        children=[],
                    )
                p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

        elif p[2] == "%=":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

            else:
                if equal(p[1].type, p[3].type) != "":
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=equal(p[1].type, p[3].type),
                        children=[],
                    )
                    p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        p[1].line_num,
                        "COMPILATION ERROR : Incompatible data type with "
                        + p[2]
                        + " operator",
                    )

        elif p[2] == "&=" or p[2] == "|=" or p[2] == "^=":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

            else:
                if equal(p[1].type, p[3].type) != "":
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=equal(p[1].type, p[3].type),
                        children=[],
                    )
                    p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        p[1].line_num,
                        "COMPILATION ERROR : Incompatible data type with "
                        + p[2]
                        + " operator",
                    )

        elif p[2] == "=":
            if p[1].type == p[3].type:
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].ast = add_edges(p)

            elif p[1].type == "STRING" and p[3].type == "stringconst":
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].ast = add_edges(p)

            elif p[1].type == "BOOL" and p[3].type == "boolconst":
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].ast = add_edges(p)

            elif p[1].type in ["FLOAT32", "FLOAT64"] and p[3].type in [
                "floatconst",
                "intconst",
            ]:
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].ast = add_edges(p)

            elif p[1].type in [
                "INT",
                "INT8",
                "INT16",
                "INT32",
                "INT64",
            ]:  # and p[3].type in ["intconst"]:
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].ast = add_edges(p)

            else:
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with assignment",
                )


### COVER ALL HERE
def p_assign_op(p):
    """assign_op : RIGHT_SHIFT_EQUAL
    | LEFT_SHIFT_EQUAL
    | PLUS_ASSIGN
    | MINUS_ASSIGN
    | STAR_ASSIGN
    | DIV_ASSIGN
    | MOD_ASSIGN
    | AND_ASSIGN
    | OR_ASSIGN
    | XOR_ASSIGN
    | ASSIGN"""
    p[0] = p[1]
    p[0] = add_edges(p)


## ExpressionList
def p_ExpressionList(p):
    """
    ExpressionList  :  Expression COMMA ExpressionList
                    | Expression
    """
    if len(p) == 2:
        # left val empty here for now
        p[0] = Node(
            name="ArgumentExpressionList",
            val=p[1].val,
            line_num=p[1].line_num,
            type=p[1].type,
            children=[p[1]],
        )
        p[0].ast = add_edges(p)
    else:
        # check if name will always be equal to ArgumentExpressionList
        # heavy doubt
        p[0] = p[3]
        p[0].children.append(p[1])
        p[0].ast = add_edges(p, [2])


## Primary Expression


def p_PrimaryExpr_1(p):  # DONE
    """PrimaryExpr : Operand"""
    p[0] = p[1]
    p[0].ast = add_edges(p)


# array accessing
def p_PrimaryExpr_2(p):
    """PrimaryExpr : PrimaryExpr Index"""

    array_type = p[1].type.split()
    if len(array_type) <= 2:
        print_compilation_error(
            "COMPILATION ERROR at line ",
            str(p[1].line_num),
            ", incorrect number of dimensions specified for " + p[1].val,
        )

    new_type = ""
    i = 2
    while i < len(array_type):
        new_type += " " + array_type[i]
        i = i + 1
    p[0] = Node(
        name="ArrayExpression",
        val=p[1].val,
        line_num=p[1].line_num,
        type=new_type.strip(),
        children=[p[1], p[2].children],
    )

    p[0].array = copy.deepcopy(p[1].array)  # check its use , now or future .
    p[0].array.append(p[2].val)
    p[0].level = p[1].level - 1
    p[0].ast = add_edges(p)
    if p[0].level == -1:
        print_compilation_error(
            "COMPILATION ERROR at line ",
            str(p[1].line_num),
            ", incorrect number of dimensions specified for " + p[1].val,
        )

    if not isint(p[2].type):
        print_compilation_error(
            "Compilation Error: Array index at line ",
            p[3].line_num,
            " is not of compatible type",
        )


def p_PrimaryExpr_3(p):  # DONE
    """Index : LEFT_SQUARE Expression RIGHT_SQUARE"""
    p[0] = Node(
        name="ArrayIndexing",
        val=p[2].val,
        line_num=p.lineno(1),
        type=p[2].type,
        children=p[2],
    )
    p[0].ast = add_edges(p)


# Slice accesing
def p_PrimaryExpr_8(p):  # same doubts as array
    """PrimaryExpr : PrimaryExpr Slice"""
    p[0] = Node(
        name="SliceExpression",
        val=p[1].val,
        line_num=p[1].line_num,
        type=p[1].type,
        children=[p[1], p[2].children],
    )
    p[0].slice = copy.deepcopy(p[1].slice)
    p[0].slice.append(p[2].val)
    p[0].level = p[1].level - 1
    # new things might have to be added , append etc.
    p[0].ast = add_edges(p)
    if p[0].level == -1:
        print_compilation_error(
            "COMPILATION ERROR at line ",
            str(p[1].line_num),
            ", incorrect number of dimensions specified for " + p[1].val,
        )

    if not isint(p[2].type):  # change this to handle 2:3 , :4 etc.
        print_compilation_error(
            "Compilation Error: Slice index at line ",
            p[3].line_num,
            " is not of compatible type",
        )


def p_PrimaryExpr_4(p):  # DONE
    """Slice  :  LEFT_SQUARE Expression  COLON Expression  RIGHT_SQUARE
    |  LEFT_SQUARE  COLON  Expression  RIGHT_SQUARE
    |  LEFT_SQUARE COLON RIGHT_SQUARE"""

    if len(p) == 4:
        p[0] = Node(
            name="SLiceIndexing",
            val=p[2].val,
            line_num=p[2].line_num,
            type="int",
            children=p[2].val,
        )
        p[0].ast = add_edges(p)

    if len(p) == 6:
        if not (isint(p[2].type) and isint(p[4].type)):
            p[0] = Node(
                name="SLiceIndexing",
                val="",
                line_num=p[2].line_num,
                type="error",
                children=[p[2], p[4]],
            )
            p[0].ast = add_edges(p)
        else:
            p[0] = Node(
                name="SLiceIndexing",
                val="",
                line_num=p[2].line_num,
                type=equal(p[2].type, p[4].type),
                children=[p[2], p[4]],
            )  # val=?? , type = ??
            p[0].ast = add_edges(p)

    if len(p) == 5:
        if not isint(p[3]):
            p[0] = Node(
                name="SLiceIndexing",
                val=p[3].val,
                line_num=p[3].line_num,
                type="error",
                children=[p[3]],
            )
            p[0].ast = add_edges(p)
        else:
            p[0] = Node(
                name="SLiceIndexing",
                val=p[3].val,
                line_num=p[3].line_num,
                type=p[3].type,
                children=[p[3]],
            )
            p[0].ast = add_edges(p)


def p_PrimaryExpr_5(p):  # DONE
    """Slice  :  LEFT_SQUARE Expression  COLON RIGHT_SQUARE"""
    if not isint(p[2].type):
        p[0] = Node(
            name="SLiceIndexing",
            val=p[2].val,
            line_num=p[2].line_num,
            type="error",
            children=[p[2]],
        )
        p[0].ast = add_edges(p)
    else:
        p[0] = Node(
            name="SLiceIndexing",
            val=p[2].val,
            line_num=p[2].line_num,
            type=p[2].type,
            children=[p[2]],
        )
        p[0].ast = add_edges(p)


def p_PrimaryExpr_6(p):  # to check this with antreev
    """PrimaryExpr :  PrimaryExpr LEFT_PARENTH RIGHT_PARENTH
    |  PrimaryExpr LEFT_PARENTH ExpressionList RIGHT_PARENTH"""
    if len(p) == 4:
        p[0] = Node(
            name="FunctionCall",
            val=p[1].val,
            line_num=p[1].line_num,
            type=p[1].type,
            children=[p[1]],
        )
        p[0].ast = add_edges(p, [2, 3])
        if (
            p[1].val not in SYMBOL_TABLE[0].keys()
            or "func" not in SYMBOL_TABLE[0][p[1].val].keys()
        ):
            print_compilation_error(
                "COMPILATION ERROR at line "
                + str(p[1].line_num)
                + ": no function with name "
                + p[1].val
                + " declared"
            )

        elif len(SYMBOL_TABLE[0][p[1].val]["argumentList"]) != 0:
            print_compilation_error(
                "Syntax Error at line",
                p[1].line_num,
                "Incorrect number of arguments for function call",
            )

    if len(p) == 5:  # check with antreev
        p[0] = Node(
            name="FunctionCall",
            val=p[1].val,
            line_num=p[1].line_num,
            type=p[1].type,
            children=[],
        )
        p[0].ast = add_edges(p, [2, 4])
        if (
            p[1].val not in SYMBOL_TABLE[0].keys()
            or "func" not in SYMBOL_TABLE[0][p[1].val].keys()
        ):
            print_compilation_error(
                "COMPILATION ERROR at line :"
                + str(p[1].line_num)
                + ": no function with name "
                + p[1].val
                + " declared"
            )

        elif len(SYMBOL_TABLE[0][p[1].val]["argumentList"]) != len(p[3].children):
            print_compilation_error(
                "Syntax Error at line "
                + str(p[1].line_num)
                + " Incorrect number of arguments for function call"
            )

        else:
            i = 0

            for arguments in SYMBOL_TABLE[0][p[1].val]["argumentList"]:
                if equal(arguments, p[3].children[i].type) == "":
                    print_compilation_error(
                        "COMPILATION ERROR at line "
                        + str(p[1].line_num)
                        + ": Type mismatch in argument "
                        + str(i + 1)
                        + " of function call, "
                        + "actual type : "
                        + arguments
                        + ", called with : "
                        + p[3].children[i].type
                    )
                    i += 1


def p_PrimaryExpr_7(p):
    """PrimaryExpr : PrimaryExpr DOT IDENTIFIER"""
    lexeme = ""
    if p[3] is tuple:
        lexeme = p[3][0]
    else:
        lexeme = p[3]

    # if not p[1].name.startswith("Period"):  #  a.x
    #     struct_scope = find_scope(p[1].val, p[1].line_num)
    #     if struct_scope == -1 or p[1].val not in SYMBOL_TABLE[struct_scope].keys():
    #         print_compilation_error(
    #             "COMPILATION ERROR at line "
    #             + str(p[1].line_num)
    #             + " : "
    #             + p[1].val
    #             + " not declared"
    #         )

    p[0] = Node(
        name="PeriodExpression",
        val=lexeme,
        line_num=p[1].line_num,
        type=p[1].type,
        children=[],
    )
    p[0].ast = add_edges(p)
    struct_name = p[1].type
    if not struct_name.startswith("struct"):
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[1].line_num)
            + ", "
            + p[1].val
            + " is not a struct"
        )

    found_scope = find_scope(struct_name, p[1].line_num)

    if found_scope == -1:
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[1].line_num)
            + ", No structure with name "
            + struct_name
        )

    flag = 0

    for curr_list in SYMBOL_TABLE[found_scope][struct_name]["field_list"]:
        if curr_list[0] == lexeme:
            flag = 1
            if curr_list[1].startswith("ARRAY"):  # to handle slices as well
                i = 0
                p[0].type = curr_list[1]
                temp = curr_list[1].split()
                dim = []
                while temp[i] == "ARRAY":
                    i = i + 1
                    dim.append(int(temp[i]))
                    i = i + 1
                p[0].level = len(dim)
            # p[0].type = temp[i]
            else:
                p[0].type = curr_list[1]
    if flag == 0:
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[1].line_num)
            + " : field "
            + " not declared in "
            + struct_name
        )


def p_Operand_1(p):  # DONE
    """Operand : IDENTIFIER"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    p[0] = Node(name="Operand", val=lexeme, line_num=p.lineno(1), type="", children=[])
    temp = find_if_ID_is_declared(lexeme, p.lineno(1))

    if temp != -1:
        p[0].type = SYMBOL_TABLE[temp][lexeme]["type"]

        # if ID is an array
        if "array" in SYMBOL_TABLE[temp][lexeme].keys():
            p[0].level = len(SYMBOL_TABLE[temp][lexeme]["array"])

        # if ID is func name
        if "func" in SYMBOL_TABLE[temp][lexeme]:
            p[0].func = 1

        # if ID is slice
        if "slice" in SYMBOL_TABLE[temp][lexeme].keys():
            p[0].level = len(SYMBOL_TABLE[temp][lexeme]["slice"])

        p[0].ast = add_edges(p)


def p_Operand_2(p):  # DONE
    """Operand : LEFT_PARENTH Expression RIGHT_PARENTH"""
    p[0] = p[2]
    p[0].ast = add_edges(p, [1, 3])


def p_Operand_3(p):  # DONE
    """Operand : Literal"""
    p[0] = p[1]
    p[0].ast = add_edges(p)


def p_Literal_1(p):  # DONE
    """Literal : BasicLit"""
    p[0] = p[1]
    p[0].ast = add_edges(p)


def p_BasicLit_1(p):  # DONE
    """BasicLit : INTCONST"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    p[0] = Node(
        name="ConstantExpression",
        val=0,
        line_num=p.lineno(1),
        type="intconst",
        children=[],
    )
    p[0].ast = add_edges(p)


def p_BasicLit_2(p):  # DONE
    """BasicLit : FLOATCONST"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    p[0] = Node(
        name="ConstantExpression",
        val=0,
        line_num=p.lineno(1),
        type="floatconst",
        children=[],
    )
    p[0].ast = add_edges(p)


def p_BasicLit_3(p):  # DONE
    """BasicLit : STRINGCONST"""
    p[0] = Node(
        name="ConstantExpression",
        val=0,
        line_num=p.lineno(1),
        type="stringconst",
        children=[],
    )
    p[0].ast = add_edges(p)


def p_BasicLit_4(p):  # DONE
    """BasicLit : BOOLCONST"""
    p[0] = Node(
        name="ConstantExpression",
        val=0,
        line_num=p.lineno(1),
        type="boolconst",
        children=[],
    )
    p[0].ast = add_edges(p)


def p_Literal_2(p):  # DONE
    """Literal : CompositeLit"""
    p[0] = p[1]
    p[0].ast = add_edges(p)


# skipping the checks here for now
# might have to add extra checks here
def p_CompositeLit(p):
    """CompositeLit : LiteralType LiteralValue"""
    p[0] = Node(
        name="CompositeLit", val="", line_num=p[1].line_num, type=p[1].type, children=[]
    )
    p[0].ast = add_edges(p)


def p_LiteralType(p):  # not keeping BasicType for semantic checks
    # copy code where initialization of array  , slice , struct is done (dipu)
    """LiteralType : StructType
    | ArrayType
    | SliceType
    | BasicType"""
    p[0] = Node(
        name="LiteralType", val="", line_num=p[1].line_num, type=p[1].type, children=[]
    )
    p[0].ast = add_edges(p)


def p_LiteralValue(p):  # ElementList must have elments of same type
    """LiteralValue : LEFT_BRACE ElementList RIGHT_BRACE
    | LEFT_BRACE RIGHT_BRACE"""
    p[0] = Node(name="ElementList", val="", line_num=p.lineno(1), type="", children=[])
    p[0].ast = add_edges(p)


# def p_Make_Func(p):
#     """Make_Func : MAKE LEFT_PARENTH multidimension TypeName COMMA Expression RIGHT_PARENTH"""


def p_multidimension(p):
    """multidimension : LEFT_SQUARE RIGHT_SQUARE
    | LEFT_SQUARE RIGHT_SQUARE multidimension
    """


def p_BasicType(p):  # pending
    """BasicType : UINT
    | UINT8
    | UINT16
    | UINT32
    | UINT64
    | INT
    | INT8
    | INT16
    | INT32
    | INT64
    | FLOAT32
    | FLOAT64
    | BOOL
    | STRING
    """
    p[0] = Node(
        name="TypeName", val="", type=p[1].upper(), line_num=p.lineno(1), children=[]
    )
    p[0].ast = add_edges(p)


def p_ElementList(p):  # pending
    """ElementList : Element COMMA ElementList
    | Element"""
    p[0] = Node(
        name="ElementList", val="", type=p[1].type, line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)


def p_Element(p):  # pending
    """Element : Expression
    | LiteralValue"""
    p[0] = p[1]
    p[0].ast = add_edges(p)


def p_Expression(p):
    """Expression : UnaryExpr
    | Expression OR Expression
    | Expression AND Expression
    | Expression BIT_OR Expression
    | Expression BIT_XOR Expression
    | Expression BIT_AND Expression



    | Expression EQUAL Expression
    | Expression NOT_EQUAL Expression
    | Expression LESS_EQUAL Expression
    | Expression GREATER_EQUAL Expression
    | Expression LESS Expression
    | Expression GREATER Expression

    | Expression RIGHT_SHIFT Expression
    | Expression LEFT_SHIFT Expression
    | Expression PLUS Expression
    | Expression MINUS Expression
    | Expression STAR Expression
    | Expression DIV Expression
    | Expression MOD Expression"""
    if len(p) == 2:
        p[0] = p[1]
        p[0].ast = add_edges(p)

    else:
        if p[2] == "||":
            if not (
                (p[1].type == "BOOL" or p[1].type == "boolconst")
                and (p[3].type == "BOOL" or p[3].type == "boolconst")
            ):
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

            else:
                p[0] = Node(
                    name="OR",
                    val="",
                    line_num=p[1].line_num,
                    type=equal(p[1].type, p[3].type),
                    children=[],
                )
                p[0].ast = add_edges(p)

        if p[2] == "&&":
            if not (
                (p[1].type == "BOOL" or p[1].type == "boolconst")
                and (p[3].type == "BOOL" or p[3].type == "boolconst")
            ):
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

            else:
                p[0] = Node(
                    name="AND",
                    val="",
                    line_num=p[1].line_num,
                    type=equal(p[1].type, p[3].type),
                    children=[],
                )
                p[0].ast = add_edges(p)

        if p[2] == "|" or p[2] == "^" or p[2] == "&":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

            else:
                if p[1].type == p[3].type:
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=p[1].type,
                        children=[],
                    )
                    p[0].ast = add_edges(p)
                elif p[1].type == "intconst":
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=p[3].type,
                        children=[],
                    )
                    p[0].ast = add_edges(p)
                elif p[3].type == "intconst":
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=p[1].type,
                        children=[],
                    )
                    p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        p[1].line_num,
                        "COMPILATION ERROR : Incompatible data type with "
                        + p[2]
                        + " operator",
                    )

        if p[2] == "==" or p[2] == "!=":
            if (
                equal(p[1].type, p[3].type) != ""
            ):  # should be exactly equal or atleast one is a constant
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=equal(p[1].type, p[3].type),
                    children=[],
                )
                p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

        if p[2] == "<=" or p[2] == ">=" or p[2] == "<" or p[2] == ">":
            if (
                equal(p[1].type, p[3].type) != ""
            ):  # should be exactly equal or atleast one is a constant

                if notcomparable(p[1].type):
                    print_compilation_error(
                        p[1].line_num,
                        "COMPILATION ERROR : Incomparable data type with "
                        + p[2]
                        + " operator",
                    )

                else:
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=equal(p[1].type, p[3].type),
                        children=[],
                    )
                    p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

        if p[2] == "<<" or p[2] == ">>":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

            else:
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].ast = add_edges(p)

        if p[2] == "+" or p[2] == "-" or p[2] == "*":
            if (
                equal(p[1].type, p[3].type) != ""
            ):  # should be exactly equal or atleast one is a constant

                if notcomparable(p[1].type):
                    print_compilation_error(
                        p[1].line_num,
                        "COMPILATION ERROR : Incomputable data type with "
                        + p[2]
                        + " operator",
                    )

                else:
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=equal(p[1].type, p[3].type),
                        children=[],
                    )
                    p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

        if p[2] == "/":
            if equal(p[1].type, p[3].type) != "":
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=equal(p[1].type, p[3].type),
                    children=[],
                )
                p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

        if p[2] == "%":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    p[1].line_num,
                    "COMPILATION ERROR : Incompatible data type with "
                    + p[2]
                    + " operator",
                )

            else:
                if equal(p[1].type, p[3].type) != "":
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=equal(p[1].type, p[3].type),
                        children=[],
                    )
                    p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        p[1].line_num,
                        "COMPILATION ERROR : Incompatible data type with "
                        + p[2]
                        + " operator",
                    )

    if p[0].type == "intconst":
        p[0].val = 0


def p_UnaryExpr(p):  # type casting not handled as of yet
    """UnaryExpr : PrimaryExpr
    | unary_op UnaryExpr"""

    if len(p) == 2:
        p[0] = p[1]
        p[0].ast = add_edges(p)
    else:
        # p[1] can be &,*,+,-,~,!

        if (
            p[1].val == "&"
        ):  # to check on what what can it be applied -> composite literal for example
            # no '&' child added, will deal in traversal
            p[0] = Node(
                name="AddressOfVariable",
                val=p[2].val,
                line_num=p[2].line_num,
                type=p[2].type + "*",
                children=[p[2]],
            )
            p[0].ast = add_edges(p)
            if p[2].type in ["intconst", "floatconst", "stringconst", "boolconst"]:
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p[1].line_num)
                    + " cannot dereference variable of type "
                    + p[2].type
                )

        elif p[1].val == "*":
            if not p[2].type.endswith("*"):
                print_compilation_error(
                    "COMPILATION ERROR at line "
                    + str(p[1].line_num)
                    + " cannot dereference variable of type "
                    + p[2].type
                )

            p[0] = Node(
                name="PointerVariable",
                val=p[2].val,
                line_num=p[2].line_num,
                type=p[2].type[: len(p[2].type) - 1],
                children=[p[2]],
            )
            p[0].ast = add_edges(p)

        else:  # check on what this can be applied as well
            p[0] = Node(
                name="SimpleUnaryOperation",
                val=p[2].val,
                line_num=p[2].line_num,
                type=p[2].type,
                children=[p[2]],
            )
            p[0].ast = add_edges(p)


def p_unary_op(p):
    """unary_op : PLUS
    | MINUS
    | NOT
    | BIT_XOR
    | STAR
    | BIT_AND"""
    p[0] = Node(
        name="UnaryOperator", val=p[1], line_num=p.lineno(1), type="", children=[]
    )
    p[0].ast = add_edges(p)


# def p_UnaryExpr_1(p):
#     """UnaryExpr : Type Expression"""
# 5.
def p_ShortVarDecl(p):
    """ShortVarDecl : IDENTIFIER COLON_ASSIGN Expression"""
    #    | IDENTIFIER COLON_ASSIGN Make_Func"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    # TODO handle slice
    if lexeme in SYMBOL_TABLE[_current_scope].keys():
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p.lineno(1))
            + " : "
            + lexeme
            + " already declared "
        )

    if True:
        if p[3].type == "intconst":
            p[3].type = "INT64"
        elif p[3].type == "floatconst":
            p[3].type = "FLOAT64"
        elif p[3].type == "stringconst":
            p[3].type = "STRING"
        elif p[3].type == "boolconst":
            p[3].type = "BOOL"
        # hNDLE FUNCTION TYPE
        if not p[3].type.startswith("ARRAY"):
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
        else:
            i = 0
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            temp = p[3].type.split()
            dim = []
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                i = i + 1
            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim

    p[0] = Node(name="VarSpec", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


# Function Declaration


def p_func_decl(p):
    """FunctionDecl : funcBegin FunctionName Signature  FunctionBody"""
    p[0] = Node(name="FunctionDecl", val="", type="", children=[], line_num=p.lineno(1))

    # arg_list = []
    # for i in p[3].children:
    #     arg_list.append(i.type)
    p[0].ast = add_edges(p)

    global _current_scope
    _current_scope = _parent[_current_scope]

    # check if the function already exists else add to symbol table
    # if p[2].val in SYMBOL_TABLE[0].keys():
    #     print_compilation_error(
    #         "COMPILATION ERROR at line :"
    #         + str(p[2].line_num)
    #         + ": function : "
    #         + p[2].val
    #         + " already declared"
    #     )

    # else:
    #     SYMBOL_TABLE[_current_scope][p[2].val] = {}
    #     SYMBOL_TABLE[_current_scope][p[2].val]["func"] = 1
    # SYMBOL_TABLE[_current_scope][p[2].val]["argumentList"] = arg_list
    # SYMBOL_TABLE[_current_scope][p[2].val]["type"] = p[3].type


# TODO : we have made our parser in a way that you can declare variables with same name in func body but they would overwrite the values of functions in arguments
def p_funcBegin(p):
    """funcBegin : FUNC"""
    global _current_scope
    global _next_scope
    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1

    p[0] = p[1]

    p[0] = add_edges(p)


def p_FunctionName(p):
    """FunctionName  : IDENTIFIER"""
    global _current_function_name

    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    p[0] = Node(
        name="FunctionName", val="", type="", children=[], func=1, line_num=p.lineno(1)
    )
    p[0].val = lexeme

    _current_function_name = lexeme

    if lexeme in SYMBOL_TABLE[0].keys():
        print_compilation_error(
            "COMPILATION ERROR at line :"
            + str(p.lineno(1))
            + ": function : "
            + lexeme
            + " already declared"
        )

    else:
        SYMBOL_TABLE[0][_current_function_name] = {}
        SYMBOL_TABLE[0][_current_function_name]["func"] = 1

    p[0].ast = add_edges(p)


def p_FunctionBody(p):
    """FunctionBody  : Block"""
    p[0] = Node(
        name="FunctionBody", val="", type="", children=[], line_num=p[1].line_num
    )
    p[0].ast = add_edges(p)


def p_Signature(p):
    """Signature  : Parameters Result
    | Parameters
    """
    global _current_function_name

    p[0] = Node(name="Signature", val="", type="", children=[], line_num=p[1].line_num)
    if len(p) == 2:
        p[0].type = "void"
    else:
        p[0].type = p[2].type

    global _current_function_return_type
    _current_function_return_type = p[0].type

    p[0].children = p[1].children

    arg_list = []

    ## adding arguments in symbol table
    for child in p[0].children:

        if child.val in SYMBOL_TABLE[_current_scope].keys():
            print_compilation_error(
                "COMPILATION ERROR at line :"
                + str(child.line_num)
                + " function argument already declared"
            )

        SYMBOL_TABLE[_current_scope][child.val] = {}
        SYMBOL_TABLE[_current_scope][child.val]["type"] = child.type
        arg_list.append(child.type)

        if child.type.startswith("ARRAY"):
            i = 0
            temp = child.type.split()
            dim = []
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                i = i + 1
            SYMBOL_TABLE[_current_scope][child.val]["array"] = dim

    SYMBOL_TABLE[0][_current_function_name]["argumentList"] = arg_list
    SYMBOL_TABLE[0][_current_function_name]["type"] = p[0].type
    # SYMBOL_TABLE[_current_scope][child.val]['value'] = child.children[1].val
    # SYMBOL_TABLE[_current_scope][child.val]['size'] = get_data_type_size(p[1].type)
    p[0].ast = add_edges(p)


def p_Result(p):
    """Result : Type"""
    p[0] = Node(name="Result", val="", type="", children=[], line_num=p[1].line_num)
    p[0].type = p[1].type
    p[0].ast = add_edges(p)


def p_Parameters(p):
    """Parameters : LEFT_PARENTH RIGHT_PARENTH
    | LEFT_PARENTH ParameterList RIGHT_PARENTH
    """
    p[0] = Node(name="Parameters", val="", type="", children=[], line_num=p.lineno(1))
    if len(p) == 4:
        p[0].children = p[2].children
    p[0].ast = add_edges(p)


def p_ParameterDecl(p):
    """ParameterDecl : IDENTIFIER Type"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    p[0] = Node(
        name="ParameterDecl", val="", type="", children=[], line_num=p.lineno(1)
    )
    p[0].val = lexeme
    p[0].type = p[2].type
    p[0].ast = add_edges(p)


def p_ParameterList(p):
    """ParameterList   : ParameterDecl COMMA ParameterList
    | ParameterDecl
    """
    if len(p) > 2:
        p[0] = Node(
            name="ParameterList", val="", type="", children=[], line_num=p[1].line_num
        )
        if p[3].name != "ParameterList":
            p[0].children.append(p[3])
        else:
            p[0].children = p[3].children

        p[0].children.append(p[1])
        p[0].ast = add_edges(p)
    else:
        p[0] = p[1]
        p[0].children.append(p[1])
        p[0].ast = add_edges(p)


########
## IF ##
########


def p_IfStmt(p):
    """IfStmt : IFBegin SimpleStmt SEMICOLON Expression Block
    | IFBegin SimpleStmt SEMICOLON Expression Block ELSE Block
    | IFBegin SimpleStmt SEMICOLON Expression Block ELSE IfStmt
    | IFBegin Expression Block
    | IFBegin Expression Block ELSE  IfStmt
    | IFBegin Expression Block ELSE  Block
    """
    p[0] = Node(name="IfStatment", val="", type="", children=[], line_num=p.lineno(1))
    global _current_scope
    _current_scope = _parent[_current_scope]
    p[0].ast = add_edges(p)


def p_IfBegin(p):
    """IFBegin : IF"""
    global _current_scope
    global _next_scope
    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1
    p[0] = p[1]
    p[0] = add_edges(p)


def p_SwitchStmt(p):
    """SwitchStmt : SWITCH Expression LEFT_BRACE expr_case_clause_list RIGHT_BRACE
    | SWITCH LEFT_BRACE  expr_case_clause_list RIGHT_BRACE
    """
    p[0] = Node(
        name="SwitchStatement", val="", type="", children=[], line_num=p.lineno(1)
    )

    # check if all the type match with the type of expression added in switch
    if len(p) == 6:
        if p[4] is not None:
            for child in p[4].children:
                if child.type != "default" and equal(p[2].type, child.type) == "":
                    print_compilation_error(
                        "COMPILATION ERROR at line "
                        + str(child.line_num)
                        + ", Expression type: "
                        + p[2].type
                        + "doesn't match with Case type:"
                        + child.type
                    )

    p[0].ast = add_edges(p)


def p_expr_case_clause_list(p):
    """expr_case_clause_list : ExprCaseClause EOS expr_case_clause_list
    | ExprCaseClause EOS
    """
    if len(p) > 3:
        p[0] = Node(
            name="ExprCaseClauseList",
            val="",
            type="",
            children=[],
            line_num=p[1].line_num,
        )
        p[0] = p[3]
        p[0].children.append(p[1])
        p[0].ast = add_edges(p)

    else:
        p[0] = Node(
            name="ExprCaseClauseList",
            val="",
            type="",
            children=[],
            line_num=p[1].line_num,
        )

        p[0].children.append(p[1])
        p[0].ast = add_edges(p)


##TODO why do we have a expression list here , doesn't work in go but is there in the doc
## Expression list external dependency
def p_ExprSwitchCase(p):
    """ExprSwitchCase : CASE ExpressionList
    | DEFAULT
    """
    global _current_scope
    global _next_scope
    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1

    if len(p) == 3:
        p[0] = Node(
            name="ExprSwitchCase", val="", type="", children=[], line_num=p.lineno(1)
        )
        check = True
        i = 0
        for i in range(len(p[2].children)):
            if p[2].children[i].type != p[2].children[0].type:
                check = False
        if check:
            p[0].type = p[2].children[0].type
        else:
            print_compilation_error(
                "COMPILATION ERROR at line "
                + str(p[0].line_num)
                + " labels of switch case have different type "
            )

    else:
        p[0] = Node(
            name="ExprSwitchDefault", val="", type="", children=[], line_num=p.lineno(1)
        )
        p[0].type = "default"
    p[0].ast = add_edges(p)


def p_ExprCaseClause(p):
    """ExprCaseClause : ExprSwitchCase COLON Statement"""
    p[0] = Node(
        name="ExprCaseClause", val="", type="", children=[], line_num=p[1].line_num
    )
    p[0].type = p[1].type
    p[0].ast = add_edges(p)

    global _current_scope
    _current_scope = _parent[_current_scope]


def p_ForStmt(p):
    """ForStmt : ForBegin Block
    | ForBegin Expression Block
    | ForBegin ForClause Block
    """
    p[0] = Node(name="ForLoop", val="", type="", children=[], line_num=p.lineno(1))
    global _loop_depth
    _loop_depth -= 1
    global _current_scope
    _current_scope = _parent[_current_scope]
    p[0].ast = add_edges(p)


def p_ForBegin(p):
    """ForBegin : FOR"""
    global _loop_depth
    _loop_depth += 1
    global _current_scope
    global _next_scope
    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1
    p[0] = p[1]
    p[0] = add_edges(p)


def p_ForClause(p):
    """ForClause :  SimpleStmt SEMICOLON Expression SEMICOLON SimpleStmt
    | SimpleStmt SEMICOLON             SEMICOLON SimpleStmt
    | SimpleStmt SEMICOLON             SEMICOLON
    |            SEMICOLON             SEMICOLON SimpleStmt
    | SimpleStmt SEMICOLON  Expression SEMICOLON
    |            SEMICOLON  Expression SEMICOLON SimpleStmt
    |            SEMICOLON  Expression SEMICOLON
    |            SEMICOLON             SEMICOLON
    """
    line_num = max(p[1].line_num, p.lineno(1))
    p[0] = Node(name="ForClause", val="", type="", children=[], line_num=line_num)
    p[0].ast = add_edges(p)


def p_error(p):
    if p:
        print_compilation_error(
            "Syntax error at token ", p.type, "  Line Number  ", p.lineno
        )
        # Just discard the token and tell the parser it's okay.
        parser.errok()
    else:
        print_compilation_error("Syntax error at EOF")


def dump_symbol_table():
    with open(SYMBOL_TABLE_DUMP_FILENAME, "w") as f:
        f.write(
            "Scope, Name, Val, Line Num, Type, Children, Array, Function, Level, Field List\n"
        )

    for i in range(_next_scope):
        if len(SYMBOL_TABLE[i]) > 0:
            temp_list = {}
            for key in SYMBOL_TABLE[i].keys():
                temp_list[key] = SYMBOL_TABLE[i][key]

            with open(SYMBOL_TABLE_DUMP_FILENAME, "a") as f:
                for j in range(len(temp_list)):
                    values = list(temp_list.values())[j]

                    keys = list(temp_list.keys())[j]

                    f.write(
                        f'{i}, {keys}, {values.get("val", "")}, {values.get("line_num", "")}, {values.get("type", "")}, {values.get("children", "")}, {values.get("array", "")}, {values.get("func", "")}, {values.get("level", "")}, {values.get("field_list", "")}\n'
                    )


parser = yacc.yacc()


def main():
    try:
        argparser = argparse.ArgumentParser(
            description="A parser for the source language that outputs the Parser Automaton in a graphical form."
        )
        argparser.add_argument("filepath", type=str, help="Path for your go program")
        args = argparser.parse_args()

        with open(args.filepath) as f:
            program = f.read().rstrip() + "\n"

        print("> Parser initiated")

        print("> AST dotfile generation initiated")

        with open(AST_FILENAME, "w") as f:
            f.write("digraph G {")

        parser = yacc.yacc()
        result = parser.parse(program)

        print("> Parser ended")

        with open(AST_FILENAME, "a") as f:
            f.write("\n}")

        print("> AST dotfile generation ended")

        print("> SYMBOL TABLE:")
        pprint(SYMBOL_TABLE)

        graphs = pydot.graph_from_dot_file(AST_FILENAME)
        graph = graphs[0]
        graph.write_png(AST_PLOT_FILENAME)

        dump_symbol_table()

        print(
            f"> Dump of the Symbol Table has been saved as '{SYMBOL_TABLE_DUMP_FILENAME}'"
        )
        print(f"> Dump of the AST has been saved as '{AST_FILENAME}'")
        print(f"> Dump of the AST has been plotted in '{AST_PLOT_FILENAME}'")

        print_success(
            Format.success + "Semantic Analysis done successfully" + Format.end
        )

        return 0

    except Exception as e:
        print_failure(Format.fail + str(e) + Format.end)

        return -1


if __name__ == "__main__":
    sys.exit(main())
