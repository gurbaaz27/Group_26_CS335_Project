###########################
## Milestone 5 : CS335A ##
######################################
## Submission Date : April 10, 2022 ##
######################################

__author__ = "Group 26, CS335A"
__filename__ = "parser.py"
__description__ = "A parser for the source language that outputs the Parser Automaton in a graphical form."

import os
import sys
import argparse
from pprint import pprint
import ply.yacc as yacc
from lexer import tokens
from constants import (
    IRCODE_FILENAME,
    SYMBOL_TABLE_DUMP_FILENAME,
    AST_FILENAME,
    AST_PLOT_FILENAME,
)
from classes import Node
from utils import (
    write_ircode,
    write_label,
    write_edge,
    ignore_lexer_literal,
    print_compilation_error,
    print_success,
    print_failure,
    operate,
    convertible,
    isint,
    notcomparable,
    equal,
)
import pydot
import copy

######################
## Global Variables ##
######################

## file io related

_symbol_table_dump_filename = ""
_ast_filename = ""
_ast_plot_filename = ""
_ircode_filename = ""

## compiler related

SYMBOL_TABLE = []
SYMBOL_TABLE.append({})

_3ac_code = ""

_global_sp = 0
_current_size = {}

_current_function_return_type = ""
_current_function_name = ""

_current_scope = 0
_next_scope = 1

_parent = {}
_parent[0] = 0

_DSU_parent = {}
_DSU_urank = {}

_loop_depth = 0
_switch_depth = 0
_current_switch_place = ""
_exit_label_switch = ""
_return_label = ""
_break_label = {}
_continue_label = {}

_current_number = 0

_label_counter = 0
_token_counter = 0

_offset = {}
_size = {
    "INT8": 1,
    "INT16": 2,
    "INT32": 4,
    "INT64": 8,
    "INT": 8,
    "UINT8": 1,
    "UINT16": 2,
    "UINT32": 4,
    "UINT64": 8,
    "UINT": 8,
    "FLOAT32": 4,
    "FLOAT64": 8,
    "BOOL": 1,
    "STRING": 100,
}

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


def DSU_create(i):
    _DSU_parent[i] = i
    _DSU_urank[i] = 1
    return


def DSU_find(i):
    if _DSU_parent[i] != i:
        _DSU_parent[i] = DSU_find(_DSU_parent[i])
    return _DSU_parent[i]


def DSU_merge(x, y):
    xroot = DSU_find(x)
    yroot = DSU_find(y)
    if xroot == yroot:
        return
    if _DSU_urank[xroot] < _DSU_urank[yroot]:
        _DSU_parent[xroot] = yroot
    elif _DSU_urank[xroot] > _DSU_urank[yroot]:
        _DSU_parent[yroot] = xroot
    else:
        _DSU_parent[yroot] = xroot
        _DSU_urank[xroot] = _DSU_urank[xroot] + 1
    return


def get_token():
    global _token_counter
    _token_counter += 1
    return "t" + str(_token_counter - 1)


def generate_label():
    global _label_counter
    label = "LABEL " + str(_label_counter)
    _label_counter = _label_counter + 1
    DSU_create(label)
    return label


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

        write_label(_ast_filename, str(p_count), stripped_p_.replace('"', ""))

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
                        write_edge(_ast_filename, str(p_count), str(p[child][1]))
                else:
                    if ignore_lexer_literal(p[child]) is False:
                        _current_number += 1
                        write_label(
                            _ast_filename,
                            str(_current_number),
                            str(p[child]).replace('"', ""),
                        )
                        p[child] = (p[child], _current_number)
                        write_edge(_ast_filename, str(p_count), str(p[child][1]))
            else:
                if type(p[child].ast) is tuple:
                    if ignore_lexer_literal(p[child].ast[0]) is False:
                        write_edge(_ast_filename, str(p_count), str(p[child].ast[1]))
                else:
                    if ignore_lexer_literal(p[child].ast) is False:
                        _current_number += 1
                        write_label(
                            _ast_filename,
                            str(_current_number),
                            str(p[child].ast).replace('"', ""),
                        )
                        p[child].ast = (p[child].ast, _current_number)
                        write_edge(_ast_filename, str(p_count), str(p[child].ast[1]))

        return stripped_p_, p_count

    else:
        if type(p[1]) is Node:
            return p[1].ast
        else:
            return p[1]


def declared_indentifier(id, lineno):
    curscp = _current_scope
    while _parent[curscp] != curscp:
        if id in SYMBOL_TABLE[curscp].keys():
            return curscp
        curscp = _parent[curscp]
    if curscp == 0:
        if id in SYMBOL_TABLE[curscp].keys():
            return curscp

    print_compilation_error(
        str(lineno) + "COMPILATION ERROR: unary_expression " + str(id) + " not declared"
    )


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


def p_start(p):
    """start : SourceFile"""
    global _3ac_code

    p[0] = p[1]
    _3ac_code = p[0].code


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
            "Compilation Error: Array index at line "
            + str(p.lineno(1))
            + " is not of compatible type",
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
    global _current_size

    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    _current_size[_current_scope] = 0
    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1

    p[0] = p[1]
    p[0] = add_edges(p)


def p_Block(p):
    """Block : LopenBrace StatementList RIGHT_BRACE"""
    global _current_scope
    global _global_sp
    global _current_size

    _global_sp -= _current_size[_current_scope]
    _current_scope = _parent[_current_scope]

    p[0] = Node(name="Block", val="", line_num=p.lineno(1), type="", children=[])
    p[0].ast = add_edges(p)

    if type(p[2]) is Node:
        if p[2].name == "StatementList":
            p[0].code = p[2].code


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
            p[0].code = p[1].code + p[3].code
        else:
            p[0].ast = add_edges(p, [2, 3])
            p[0].code = p[1].code


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
    p[0].code = p[1].code


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
                + str(p[2].type)
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
    global _break_label

    p[0] = Node(name="BreakStmt", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)
    if p[2].type != "intconst":
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[0].line_num)
            + "argument to  break should be a constant"
        )

    if _loop_depth == 0 or _switch_depth == 0:
        print_compilation_error(str(p[0].line_num) + " : break not inside loop")

    if len(p) == 3:
        if p[2].place > _loop_depth:
            print_compilation_error(
                str(p[0].line_num) + " : breaking index more than number of loop"
            )

        p[0].code = [["goto", _break_label[_loop_depth + 1 - int(p[2].place)]]]
    else:
        p[0].code = [["goto", _break_label[_loop_depth]]]


## CONTINUE STATEMENT
def p_ContinueStmt(p):
    """ContinueStmt : CONTINUE"""
    global _loop_depth
    global _continue_label

    p[0] = Node(name="ContinueStmt", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)

    if _loop_depth == 0:
        print_compilation_error(str(p[0].line_num) + " : continue not inside loop")

    p[0].code = [["goto", _continue_label[_loop_depth]]]


## DECLARATION
def p_Declaration(p):
    """Declaration : ConstDecl
    | TypeDecl
    | VarDecl"""
    p[0] = Node(
        name="Declaration", val="", type="", line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)
    p[0].code = p[1].code


def p_TopLevelDecl(p):
    """TopLevelDecl : Declaration
    | FunctionDecl"""
    p[0] = Node(
        name="TopLevelDecl", val="", type="", line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)
    p[0].code = p[1].code


def p_TopLevelDeclList_1(p):
    """TopLevelDeclList : TopLevelDecl EOS TopLevelDeclList
    | TopLevelDecl"""
    p[0] = Node(
        name="TopLevelDeclList", val="", type="", line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)

    if len(p) == 2:
        p[0].code = p[1].code
    else:
        p[0].code = p[1].code + p[3].code


def p_TopLevelDeclList_2(p):
    """TopLevelDeclList : empty"""
    p[0] = Node(name="TopLevelDeclList", val="", type="", children=[])
    p[0].ast = add_edges(p)


def p_SourceFile(p):
    """SourceFile : TopLevelDeclList"""
    p[0] = Node(name="SourceFile", val="", type="", line_num=p[1].line_num, children=[])
    p[0].ast = add_edges(p)
    p[0].code = p[1].code


## 1. ConstDecl
def p_ConstDecl(p):
    """ConstDecl : CONST ConstSpec"""
    p[0] = Node(name="ConstDecl", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)
    p[0].code = p[2].code


def p_ConstSpec(p):
    """ConstSpec : IDENTIFIER Type ASSIGN Expression
    | IDENTIFIER ASSIGN Expression"""
    global _global_sp
    global _current_size

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
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1
            if p[2].type.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += 8
                _global_sp += 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = _size[p[2].type]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += _size[p[2].type]
                _global_sp += _size[p[2].type]

            p[0].code = p[4].code
            if p[2].type.endswith("*") or p[2].type in [
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
                "BOOL",
            ]:
                p[0].code.append(["int_copy", lexeme, p[4].place])
            elif p[2].type in ["FLOAT32", "FLOAT64"]:
                p[0].code.append(["float_copy", lexeme, p[4].place])
            elif p[2].type in ["STRING"]:
                p[0].code.append(["string_copy", lexeme, p[4].place])
            elif p[4].type == "intconst":
                p[0].code.append(["int_copy_immediate", lexeme, p[4].place])
            elif p[4].type == "floatconst":
                p[0].code.append(["float_copy_immediate", lexeme, p[4].place])
            elif p[4].type == "boolconst":
                if p[4].place == "True":
                    p[0].code.append(["load immediate", lexeme, "1"])
                else:
                    p[0].code.append(["load immediate", lexeme, "0"])
            elif p[4].type == "stringconst":
                p[0].code.append(["string_copy_immediate", lexeme, p[4].place])

        else:
            # Pass complete array string
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
            i = 0
            temp = p[3].type.split()
            dim = []
            Quant = 1
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                Quant *= int(temp[i])
                i = i + 1
            typ = temp[i]
            if typ == "struct":
                typ = typ + " " + temp[i + 1]
            if typ.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * 8
                _global_sp += Quant * 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * _size[typ]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * _size[typ]
                _global_sp += Quant * _size[typ]

            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1

    elif len(p) == 4:
        if not p[3].type.startswith("ARRAY"):
            p[0].code = p[3].code
            if p[3].type.endswith("*") or p[3].type in [
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
                "BOOL",
            ]:
                p[0].code.append(["int_copy", lexeme, p[3].place])
            elif p[3].type in ["FLOAT32", "FLOAT64"]:
                p[0].code.append(["float_copy", lexeme, p[3].place])
            elif p[3].type in ["STRING"]:
                p[0].code.append(["string_copy", lexeme, p[3].place])
            elif p[3].type == "intconst":
                p[0].code.append(["int_copy_immediate", lexeme, p[3].place])
            elif p[3].type == "floatconst":
                p[0].code.append(["float_copy_immediate", lexeme, p[3].place])
            elif p[3].type == "boolconst":
                if p[3].place == "True":
                    p[0].code.append(["load immediate", lexeme, "1"])
                else:
                    p[0].code.append(["load immediate", lexeme, "0"])
            elif p[3].type == "stringconst":
                p[0].code.append(["string_copy_immediate", lexeme, p[3].place])
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
            if p[3].type.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += 8
                _global_sp += 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = _size[p[3].type]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += _size[p[3].type]
                _global_sp += _size[p[3].type]
        else:
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            i = 0
            temp = p[3].type.split()
            dim = []
            Quant = 1
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                Quant *= int(temp[i])
                i = i + 1
            typ = temp[i]
            if typ == "struct":
                typ = typ + " " + temp[i + 1]
            if typ.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * 8
                _global_sp += Quant * 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * _size[typ]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * _size[p[3].type]
                _global_sp += Quant * _size[p[3].type]

            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim
            SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1

    # else:
    #     if not p[2].type.startswith("ARRAY"):
    #         SYMBOL_TABLE[_current_scope][lexeme] = {}
    #         SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
    #         SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1
    #         SYMBOL_TABLE[_current_scope][lexeme]["size"] =_size[p[2].type]
    #         if(p[2].type.endswith("*")):
    #             SYMBOL_TABLE[_current_scope][lexeme]["size"] = 8
    #     else:
    #         # Pass complete array string
    #         SYMBOL_TABLE[_current_scope][lexeme] = {}
    #         SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
    #         i = 0
    #         temp = p[3].type.split()
    #         dim = []
    #         while temp[i] == "ARRAY":
    #             i = i + 1
    #             dim.append(int(temp[i]))
    #             i = i + 1
    #         SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim
    #         SYMBOL_TABLE[_current_scope][lexeme]["const"] = 1

    p[0] = Node(name="ConstSpec", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


## 2. Typedecl
def p_TypeDecl(p):
    """TypeDecl : TYPE TypeSpec"""
    p[0] = Node(name="TypeDecl", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)
    p[0].code = p[2].code


def p_TypeSpec(p):
    """TypeSpec : AliasDecl
    | TypeDef"""
    p[0] = Node(name="TypeSpec", val="", type="", line_num=p[1].line_num, children=[])
    p[0].ast = add_edges(p)
    p[0].code = p[1].code


def p_AliasDecl(p):
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
    names = []
    i = 2
    CurrSize = 0
    _offset[sym] = {}
    while i < len(temp):
        if temp[i] in names:
            print_compilation_error(
                "COMPILATION ERROR at line "
                + str(p[2].line_num)
                + " : "
                + "Name "
                + temp[i]
                + " Already declared"
            )
        curr = []
        curr.append(temp[i])
        names.append(temp[i])
        _offset[sym][temp[i]] = CurrSize
        i = i + 1
        typ = ""
        Quant = 1
        while temp[i] == "ARRAY":
            typ = typ + " ARRAY"
            i = i + 1
            # dim.append(int(temp[i]))
            typ = typ + " " + temp[i]
            Quant *= int(temp[i])
            i = i + 1
        isStruct = ""
        if temp[i] == "struct":
            typ = typ + " struct"
            i = i + 1
            isStruct = "struct "
        if temp[i].endswith("*"):
            CurrSize += Quant * 8
        else:
            CurrSize += Quant * _size[isStruct + temp[i]]
        typ = typ + " " + temp[i]
        i = i + 1
        curr.append(typ.strip())
        fields.append(curr)
    _size[sym] = CurrSize
    SYMBOL_TABLE[_current_scope][sym] = {}
    SYMBOL_TABLE[_current_scope][sym]["field_list"] = fields
    SYMBOL_TABLE[_current_scope][sym]["size"] = CurrSize

    p[0] = Node(name="TypeDef", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)


## 3. VarDecl
def p_VarDecl(p):
    """VarDecl : VAR VarSpec"""
    p[0] = Node(name="VarDecl", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)
    p[0].code = p[2].code


## VarSpec
def p_VarSpec(p):
    """VarSpec : IDENTIFIER Type ASSIGN Expression
    | IDENTIFIER ASSIGN Expression
    | IDENTIFIER Type"""
    global _global_sp
    global _current_size

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

    p[0] = Node(name="VarSpec", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)

    if len(p) == 5:
        if p[2].type != p[4].type:
            if p[4].type not in ["intconst", "floatconst", "stringconst", "boolconst"]:

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
            if p[2].type.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += 8
                _global_sp += 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = _size[p[2].type]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += _size[p[2].type]
                _global_sp += _size[p[2].type]

            p[0].code = p[4].code
            if p[2].type.endswith("*") or p[2].type in [
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
                "BOOL",
            ]:
                p[0].code.append(["int_copy", lexeme, p[4].place])
            elif p[2].type in ["FLOAT32", "FLOAT64"]:
                p[0].code.append(["float_copy", lexeme, p[4].place])
            elif p[2].type in ["STRING"]:
                p[0].code.append(["string_copy", lexeme, p[4].place])
            elif p[4].type == "intconst":
                p[0].code.append(["int_copy_immediate", lexeme, p[4].place])
            elif p[4].type == "floatconst":
                p[0].code.append(["float_copy_immediate", lexeme, p[4].place])
            elif p[4].type == "boolconst":
                if p[4].place == "True":
                    p[0].code.append(["load immediate", lexeme, "1"])
                else:
                    p[0].code.append(["load immediate", lexeme, "0"])
            elif p[4].type == "stringconst":
                p[0].code.append(["string_copy_immediate", lexeme, p[4].place])

        else:
            # Pass complete array string
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
            i = 0
            temp = p[2].type.split()
            dim = []
            Quant = 1
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                Quant *= int(temp[i])
                i = i + 1
            typ = temp[i]
            if typ == "struct":
                typ = typ + " " + temp[i + 1]
            if typ.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += 8
                _global_sp += 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * _size[typ]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * _size[typ]
                _global_sp += Quant * _size[typ]

            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim

    elif len(p) == 4:
        if not p[3].type.startswith("ARRAY"):
            p[0].code = p[3].code
            if p[3].type.endswith("*") or p[3].type in [
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
                "BOOL",
            ]:
                p[0].code.append(["int_copy", lexeme, p[3].place])
            elif p[3].type in ["FLOAT32", "FLOAT64"]:
                p[0].code.append(["float_copy", lexeme, p[3].place])
            elif p[3].type in ["STRING"]:
                p[0].code.append(["string_copy", lexeme, p[3].place])
            elif p[3].type == "intconst":
                p[0].code.append(["int_copy_immediate", lexeme, p[3].place])
            elif p[3].type == "floatconst":
                p[0].code.append(["float_copy_immediate", lexeme, p[3].place])
            elif p[3].type == "boolconst":
                if p[3].place == "True":
                    p[0].code.append(["load immediate", lexeme, "1"])
                else:
                    p[0].code.append(["load immediate", lexeme, "0"])
            elif p[3].type == "stringconst":
                p[0].code.append(["string_copy_immediate", lexeme, p[3].place])
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
            if p[3].type.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += 8
                _global_sp += 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = _size[p[3].type]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += _size[p[3].type]
                _global_sp += _size[p[3].type]
        else:
            i = 0
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            temp = p[3].type.split()
            dim = []
            Quant = 1
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                Quant *= int(temp[i])
                i = i + 1
            typ = temp[i]
            if typ == "struct":
                typ = typ + " " + temp[i + 1]
            if typ.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * 8
                _global_sp += Quant * 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * _size[typ]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * _size[typ]
                _global_sp += Quant * _size[typ]

            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim

    else:
        if not p[2].type.startswith("ARRAY"):
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
            if p[2].type.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += 8
                _global_sp += 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = _size[p[2].type]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += _size[p[2].type]
                _global_sp += _size[p[2].type]
        else:
            # Pass complete array string
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[2].type
            i = 0
            temp = p[2].type.split()
            dim = []
            Quant = 1
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                Quant *= int(temp[i])
                i = i + 1
            typ = temp[i]
            if typ == "struct":
                typ = typ + " " + temp[i + 1]
            if typ.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * 8
                _global_sp += Quant * 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * _size[typ]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * _size[typ]
                _global_sp += Quant * _size[typ]

            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim


## SIMPLE STATEMENT
def p_SimpleStmt(p):
    """SimpleStmt : ExpressionStmt
    | IncDecStmt
    | Assignment
    | ShortVarDecl"""
    p[0] = Node(name="SimpleStmt", val="", type="", line_num=p[1].line_num, children=[])
    p[0].ast = add_edges(p)
    p[0].code = p[1].code


def p_ExpressionStmt(p):
    """ExpressionStmt : Expression"""
    p[0] = Node(
        name="ExpressionStmt", val="", type="", line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)
    p[0].code = p[1].code


# 3.
def p_IncDecStmt(p):  # to check on which all things can this be applied
    """IncDecStmt : Expression INCREMENT
    | Expression DECREMENT"""
    lexeme = ""
    if type(p[2]) is tuple:
        lexeme = p[2][0]
    else:
        lexeme = p[2]

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
            "Compilation Error at line" 
            + str(p[1].line_num),
            + ": Invalid operation on",
            + str(p[1].val),
        )
    else:
        if (p[1].func == 1) or ("struct" in p[1].type.split()):
            print_compilation_error(
                "Compilation Error at line"
                + str(p[1].line_num)
                + ": Invalid operation on"
                + str(p[1].val)
            )

        elif p[1].level != 0:
            print_compilation_error(
                "Compilation Error at line"
                + str(p[1].line_num)
                + ": Invalid operation on"
                + str(p[1].val)
            )

        else:
            if isint(p[1].type) and p[1].type != "intconst":
                p[0].code = p[1].code
                if lexeme == "++":
                    p[0].code.append(["int immediate +", p[0].place, p[1].place, "1"])
                else:
                    p[0].code.append(["int immediate +", p[0].place, p[1].place, "-1"])
            else:
                print_compilation_error(
                    "Compilation Error at line"
                    + str(p[1].line_num)
                    + ":Invalid operation on"
                    + str(p[1].val)
                )


# def p_Assignment_1(p):
#     """Assignment : Expression assign_op Make_Func"""
#     pass


def p_Assignment_2(p):
    """Assignment : Expression assign_op Expression"""

    if p[1].type in ["intconst", "floatconst", "boolconst", "stringconst"]:
        print_compilation_error(
            str(p[1].line_num) + "COMPILATION ERROR : Left hand side cannot be constant"
        )

    else:
        if p[2] == ">>=" or p[2] == "<<=":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    str(p[1].line_num)
                    + " COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
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
                if p[1].type == "intconst":
                    print_compilation_error(
                        str(p[1].line_num)
                        + "COMPILATION ERROR : Cannot apply "
                        + str(p[2])
                        + " with "
                        + str(p[1].type)
                    )

                else:
                    if p[3].type == "intconst":
                        p[0].code = p[1].code
                        p[0].place = get_token()
                        p[0].code.append(
                            [p[2] + "logical", p[0].place, p[1].place, p[3].place]
                        )
                        p[0].ast = add_edges(p)
                    else:
                        p[0].code = p[1].code + p[3].code
                        p[0].place = get_token()
                        p[0].code.append(
                            [p[2] + "variable", p[0].place, p[1].place, p[3].place]
                        )
                        p[0].ast = add_edges(p)

        elif p[2] == "+=" or p[2] == "-=" or p[2] == "*=":
            if (
                equal(p[1].type, p[3].type) != ""
            ):  # should be exactly equal or atleast one is a constant

                if notcomparable(p[1].type):
                    print_compilation_error(
                        str(p[1].line_num)
                        + " COMPILATION ERROR : Incomputable data type with "
                        + str(p[2])
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
                    if p[1].type == "intconst" and p[3].type == "intconst":
                        p[0].val = str(operate(int(p[1].val), p[2], int(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                    elif p[1].type == "floatconst" and p[3].type == "floatconst":
                        p[0].val = str(operate(float(p[1].val), p[2], float(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                    else:
                        if p[3].type == "intconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "int" + p[2],
                                    p[0].place,
                                    p[1].place,
                                    p[3].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[3].type == "floatconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "float" + p[2],
                                    p[0].place,
                                    p[1].place,
                                    p[3].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type == "intconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "int" + p[2],
                                    p[0].place,
                                    p[3].place,
                                    p[1].place,
                                ]
                            )
                            p[0].ast = add_edges(p)

                        elif p[1].type == "floatconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "float" + p[2],
                                    p[0].place,
                                    p[3].place,
                                    p[1].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type in ["FLOAT32", "FLOAT64"]:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["float" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        else:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    str(p[1].line_num)
                    + " COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
                    + " operator",
                )

        elif p[2] == "/=":
            if equal(p[1].type, p[3].type) != "":
                if notcomparable(p[1].type):
                    print_compilation_error(
                        str(p[1].line_num)
                        + " COMPILATION ERROR : Incomputable data type with "
                        + str(p[2])
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
                    if p[1].type == "intconst" and p[3].type == "intconst":
                        p[0].val = str((int(p[1].val) // int(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                    elif p[1].type == "floatconst" and p[3].type == "floatconst":
                        p[0].val = str((float(p[1].val) / float(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                        p[0].ast = add_edges(p)
                    else:
                        if p[3].type == "intconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            temp_token = get_token()
                            p[0].code.append(
                                ["load immediate ", temp_token, p[3].place]
                            )
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, temp_token]
                            )
                            p[0].ast = add_edges(p)
                        elif p[3].type == "floatconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            temp_token = get_token()
                            p[0].code.append(
                                ["load immediate ", temp_token, p[3].place]
                            )
                            p[0].code.append(
                                ["float" + p[2], p[0].place, p[1].place, temp_token]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type == "intconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            temp_token = get_token()
                            p[0].code.append(
                                ["load immediate ", temp_token, p[1].place]
                            )
                            p[0].code.append(
                                ["int" + p[2], p[0].place, temp_token, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type == "floatconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            temp_token = get_token()
                            p[0].code.append(
                                ["load immediate ", temp_token, p[1].place]
                            )
                            p[0].code.append(
                                ["int" + p[2], p[0].place, temp_token, p[3].place]
                            )
                            p[0].ast = add_edges(p)

                        elif p[1].type in ["FLOAT32", "FLOAT64"]:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["float" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        else:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    str(p[1].line_num)
                    + " COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
                    + " operator",
                )

        elif p[2] == "%=":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    str(p[1].line_num)
                    + " COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
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
                    if p[1].type == "intconst" and p[3].type == "intconst":
                        p[0].val = str((int(p[1].val) % int(p[3].val)))
                        p[0].place = p[0].val
                        p[0].code = []
                        p[0].ast = add_edges(p)
                    else:
                        if p[1].type != "intconst" and p[3].type != "intconst":
                            p[0].code = p[1].code + p[3].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        else:
                            if p[1].type == "intconst":
                                p[0].code = p[3].code
                                p[0].place = get_token()
                                temp_token = get_token()
                                p[0].code.append(
                                    ["load immediate ", temp_token, p[1].place]
                                )
                                p[0].code.append(
                                    ["int" + p[2], p[0].place, temp_token, p[3].place]
                                )
                                p[0].ast = add_edges(p)
                            else:
                                p[0].code = p[1].code
                                p[0].place = get_token()
                                temp_token = get_token()
                                p[0].code.append(
                                    ["load immediate ", temp_token, p[3].place]
                                )
                                p[0].code.append(
                                    ["int" + p[2], p[0].place, p[1].place, temp_token]
                                )
                                p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        str(p[1].line_num)
                        + " COMPILATION ERROR : Incompatible data type with "
                        + str(p[2])
                        + " operator"
                    )

        elif p[2] == "&=" or p[2] == "|=" or p[2] == "^=":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    str(p[1].line_num)
                    + " COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
                    + " operator"
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

                    if not (p[1].type == "intconst" and p[3].type == "intconst"):
                        p[0].code = p[1].code + p[3].code
                        # p[0].code.append(p[3].code)
                        p[0].place = get_token()
                        p[0].code.append([p[2], p[0].place, p[1].place, p[3].place])
                    else:
                        p[0].val = str(operate(int(p[1].val), p[2], int(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                elif p[1].type == "intconst":
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=p[3].type,
                        children=[],
                    )
                    p[0].code = p[3].code
                    p[0].place = get_token()
                    p[0].code.append(
                        ["immediate" + p[2], p[0].place, p[3].place, p[1].place]
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
                    p[0].code = p[1].code
                    p[0].place = get_token()
                    p[0].code.append(
                        ["immediate" + p[2], p[0].place, p[1].place, p[3].place]
                    )
                    p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        str(p[1].line_num)
                        + " COMPILATION ERROR : Incompatible data type with "
                        + str(p[2])
                        + " operator"
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

                if (
                    isint(p[1].type)
                    or p[1].type in ["FLOAT32", "FLOAT64", "BOOL", "STRING"]
                    or p[1].type.endswith("*")
                ):
                    if isint(p[1].type) or p[1].type == "BOOL":
                        p[0].place = get_token()
                        p[0].code = p[1].code + p[3].code
                        p[0].code.append(["int_copy", p[0].place, p[3].place])
                        p[0].ast = add_edges(p)
                    elif p[1].type in ["FLOAT32", "FLOAT64"]:
                        p[0].place = get_token()
                        p[0].code = p[1].code + p[3].code
                        p[0].code.append(["float_copy", p[0].place, p[3].place])
                        p[0].ast = add_edges(p)
                    elif p[1].type.endswith("*"):
                        p[0].place = get_token()
                        p[0].code = p[1].code + p[3].code
                        p[0].code.append(["int_copy", p[0].place, p[3].place])
                        p[0].ast = add_edges(p)
                    else:
                        p[0].place = get_token()
                        p[0].code = p[1].code + p[3].code
                        p[0].code.append(["string_copy", p[0].place, p[3].place])
                        p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        str(p[1].line_num)
                        + " COMPILATION ERROR : Incompatible data type with assignment"
                    )

            elif p[1].type == "STRING" and p[3].type == "stringconst":
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].place = get_token()
                p[0].code = p[1].code 
                p[0].code.append(["string_copy_immediate", p[0].place, p[3].place])
                p[0].ast = add_edges(p)

            elif p[1].type == "BOOL" and p[3].type == "boolconst":
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].place = get_token()
                p[0].code = p[1].code 
                if p[3].place == "True":
                    p[0].code.append(["load immediate", p[0].place, "1"])
                else:
                    p[0].code.append(["load immediate", p[0].place, "0"])
                p[0].ast = add_edges(p)

            elif p[1].type in ["FLOAT32", "FLOAT64"] and p[3].type in [
                "floatconst",
            ]:
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].place = get_token()
                p[0].code = p[1].code 
                p[0].code.append(["float_copy_immediate", p[0].place, p[3].place])
                p[0].ast = add_edges(p)
            elif p[1].type in ["INT", "INT8", "INT16", "INT32", "INT64",] and p[
                3
            ].type in ["intconst"]:
                p[0] = Node(
                    name=p[2],
                    val="",
                    line_num=p[1].line_num,
                    type=p[1].type,
                    children=[],
                )
                p[0].place = get_token()
                p[0].code = p[1].code 
                p[0].code.append(["int_copy_immediate", p[0].place, p[3].place])
                p[0].ast = add_edges(p)

            else:
                print_compilation_error(
                    str(p[1].line_num)
                    + " COMPILATION ERROR : Incompatible data type with assignment"
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
        p[0].code = p[1].code
    else:
        # check if name will always be equal to ArgumentExpressionList
        # heavy doubt
        p[0] = p[3]
        p[0].children.append(p[1])
        p[0].ast = add_edges(p, [2])
        p[0].code = p[1].code + p[3].code


## Primary Expression


def p_PrimaryExpr_1(p):  # DONE
    """PrimaryExpr : Operand"""
    p[0] = p[1]
    p[0].ast = add_edges(p)


# array accessing
# array accessing
def p_PrimaryExpr_2(p):
    """PrimaryExpr : PrimaryExpr Index"""

    array_type = p[1].type.split()
    if len(array_type) <= 2:
        print_compilation_error(
            "COMPILATION ERROR at line ",
            str(p[1].line_num),
            ", incorrect number of dimensions specified for " 
            + p[1].val
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
    p[0].dims = p[1].dims
    p[0].code = p[1].code
    add = 1
    for i in range(len(p[0].dims) - p[0].level, len(p[0].dims)):
        add *= p[0].dims[i]
    new_type = new_type.split()
    length = len(new_type)
    type = ""
    if length == 1:
        type = new_type[0]
    else:
        if new_type[length - 2] == "struct":
            type = "struct" + " " + new_type[length - 1]
        else:
            type = new_type[length - 1]
    type_size = 0
    if type.endswith("*"):
        type_size = 8
    else:
        type_size = _size[type]

    temp_label = get_token()
    p[0].place = "*" + get_token()
    add *= type_size
    p[0].code.append(["int immediate *", temp_label, p[2].place, add])
    p[0].code.append(["int  +", p[0].place, p[1].place, temp_label])
    if p[0].level == -1:
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[1].line_num)
            + ", incorrect number of dimensions specified for " 
            + p[1].val
        )

    if not isint(p[2].type):
        print_compilation_error(
            "Compilation Error: Array index at line "
            + str(p[3].line_num)
            + " is not of compatible type"
        )


def p_PrimaryExpr_3(p):  # DONE
    """Index : LEFT_SQUARE Expression RIGHT_SQUARE"""
    p[0] = p[2]
    p[0].ast = add_edges(p, [1, 3])


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
            "COMPILATION ERROR at line "
            + str(p[1].line_num),
            + ", incorrect number of dimensions specified for " 
            + str(p[1].val)
        )

    if not isint(p[2].type):  # change this to handle 2:3 , :4 etc.
        print_compilation_error(
            "Compilation Error: Slice index at line "
            + str(p[3].line_num)
            + " is not of compatible type"
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


## TODO
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
                "Syntax Error at line"
                + str(p[1].line_num)
                + "Incorrect number of arguments for function call"
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
                        + str(arguments)
                        + ", called with : "
                        + str(p[3].children[i].type)
                    )
                    i += 1


def p_PrimaryExpr_7(p):
    """PrimaryExpr : PrimaryExpr DOT IDENTIFIER"""
    lexeme = ""
    if p[3] is tuple:
        lexeme = p[3][0]
    else:
        lexeme = p[3]
    p[0] = Node(
        name="PeriodExpression",
        val=lexeme,
        line_num=p[1].line_num,
        type=p[1].type,
        children=[],
    )
    p[0].ast = add_edges(p)
    p[0].code = p[1].code
    p[0].place = "*" + get_token()
    struct_name = p[1].type
    if not struct_name.startswith("struct"):
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[1].line_num)
            + ", "
            + str(p[1].val)
            + " is not a struct"
        )

    found_scope = find_scope(struct_name, p[1].line_num)

    if found_scope == -1:
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[1].line_num)
            + ", No structure with name "
            + str(struct_name)
        )

    flag = 0
    off = -1
    for curr_list in SYMBOL_TABLE[found_scope][struct_name]["field_list"]:
        if curr_list[0] == lexeme:
            off = _offset[struct_name][lexeme]
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
                p[0].dims = dim
            # p[0].type = temp[i]
            else:
                p[0].type = curr_list[1]
    if flag == 0:
        print_compilation_error(
            "COMPILATION ERROR at line "
            + str(p[1].line_num)
            + " : field "
            + " not declared in "
            + str(struct_name)
        )

    else:
        p[0].code.append(["int immediate + ", p[0].place, p[1].place, off])


def p_PrimaryExpr_9(p):
    """PrimaryExpr : Conversion"""
    p[0] = p[1]
    p[0].ast = add_edges(p)


def p_Conv_type(p):
    """Conv_type : UINT
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
    | FLOAT64"""

    if len(p) == 2:
        p[0] = Node(
            name="TypeName",
            val="",
            type=p[1].upper(),
            line_num=p.lineno(1),
            children=[],
        )
        p[0].ast = add_edges(p)
    else:
        p[0] = Node(
            name="PointerType",
            val="",
            type=p[2].type + "*",
            line_num=p.lineno(1),
            children=[],
        )
        p[0].ast = add_edges(p)


def p_Conversion(p):
    """Conversion : Conv_type LEFT_PARENTH Expression RIGHT_PARENTH"""
    p[0] = p[3]
    p[0].type = p[1].type
    p[0].place = get_token()
    p[0].code.append([p[1].type + "to" + p[0].type, p[0].place, p[1].place])
    p[0].ast = add_edges(p)

    if not convertible(p[3].type, p[1].type):
        print_compilation_error(
            str(p[1].line_num)
            + "COMPILATION ERROR : Cannot Type Cast"
            + str(p[3].type)
            + "into"
            + str(p[1].type)
        )


def p_Operand_1(p):  # DONE
    """Operand : IDENTIFIER"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]

    p[0] = Node(name="Operand", val=lexeme, line_num=p.lineno(1), type="", children=[])
    p[0].place = lexeme
    temp = declared_indentifier(lexeme, p.lineno(1))

    if temp != -1:
        p[0].type = SYMBOL_TABLE[temp][lexeme]["type"]

        # if ID is an array
        if "array" in SYMBOL_TABLE[temp][lexeme].keys():
            p[0].level = len(SYMBOL_TABLE[temp][lexeme]["array"])
            p[0].dims = SYMBOL_TABLE[temp][lexeme]["array"]
            # print_compilation_error(SYMBOL_TABLE[temp][lexeme]["array"])

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
        val=lexeme,
        line_num=p.lineno(1),
        type="intconst",
        children=[],
    )
    p[0].place = p[0].val
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
        val=lexeme,
        line_num=p.lineno(1),
        type="floatconst",
        children=[],
    )
    p[0].place = p[0].val
    p[0].ast = add_edges(p)


def p_BasicLit_3(p):  # DONE
    """BasicLit : STRINGCONST"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]
    p[0] = Node(
        name="ConstantExpression",
        val=lexeme,
        line_num=p.lineno(1),
        type="stringconst",
        children=[],
    )
    p[0].place = p[0].val
    p[0].ast = add_edges(p)


def p_BasicLit_4(p):  # DONE
    """BasicLit : BOOLCONST"""
    lexeme = ""
    if p[1] is tuple:
        lexeme = p[1][0]
    else:
        lexeme = p[1]
    p[0] = Node(
        name="ConstantExpression",
        val=lexeme,
        line_num=p.lineno(1),
        type="boolconst",
        children=[],
    )
    p[0].place = p[0].val
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


def p_BasicType(p):
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


def p_ElementList(p):
    """ElementList : Element COMMA ElementList
    | Element"""
    p[0] = Node(
        name="ElementList", val="", type=p[1].type, line_num=p[1].line_num, children=[]
    )
    p[0].ast = add_edges(p)

    if len(p) == 2:
        p[0].code = p[1].code
    else:
        p[0].code = p[1].code + p[3].code


def p_Element(p):
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
                    str(p[1].line_num)
                    + "COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
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
                p[0].true = generate_label()
                p[0].false = generate_label()
                DSU_merge(p[1].true, p[3].true)
                DSU_merge(p[0].true, p[1].true)
                DSU_merge(p[0].false, p[3].false)
                p[0].code = p[1].code + p[3].code
                # p[0].code.append(p[1].code)
                p[0].code.append(["BNEZ", p[1].place, p[1].true])
                # p[0].code.append(p[3].code)
                p[0].code.append(["BNEZ", p[3].place, p[3].true])
                p[0].code.append(["GOTO", p[3].false])

        if p[2] == "&&":
            if not (
                (p[1].type == "BOOL" or p[1].type == "boolconst")
                and (p[3].type == "BOOL" or p[3].type == "boolconst")
            ):
                print_compilation_error(
                    str(p[1].line_num)
                    + "COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
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
                p[0].true = generate_label()
                p[0].false = generate_label()
                DSU_merge(p[1].false, p[3].false)
                DSU_merge(p[0].false, p[1].false)
                DSU_merge(p[0].true, p[3].true)
                p[0].code = p[1].code + p[3].code
                # p[0].code.append(p[1].code)
                p[0].code.append(["BEZ", p[1].place, p[1].false])
                # p[0].code.append(p[3].code)
                p[0].code.append(["BEZ", p[3].place, p[3].false])
                p[0].code.append(["GOTO", p[3].true])

        if p[2] == "|" or p[2] == "^" or p[2] == "&":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    str(p[1].line_num)
                    + "COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
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

                    if not (p[1].type == "intconst" and p[3].type == "intconst"):
                        p[0].code = p[1].code + p[3].code
                        # p[0].code.append(p[3].code)
                        p[0].place = get_token()
                        p[0].code.append([p[2], p[0].place, p[1].place, p[3].place])
                    else:
                        p[0].val = str(operate(int(p[1].val), p[2], int(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                elif p[1].type == "intconst":
                    p[0] = Node(
                        name=p[2],
                        val="",
                        line_num=p[1].line_num,
                        type=p[3].type,
                        children=[],
                    )
                    p[0].code = p[3].code
                    p[0].place = get_token()
                    p[0].code.append(
                        ["immediate" + p[2], p[0].place, p[3].place, p[1].place]
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
                    p[0].code = p[1].code
                    p[0].place = get_token()
                    p[0].code.append(
                        ["immediate" + p[2], p[0].place, p[1].place, p[3].place]
                    )
                    p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        str(p[1].line_num)
                        + "COMPILATION ERROR : Incompatible data type with "
                        + str(p[2])
                        + " operator",
                    )

        if (
            p[2] == "=="
            or p[2] == "!="
            or p[2] == "<="
            or p[2] == ">="
            or p[2] == "<"
            or p[2] == ">"
        ):
            if (
                equal(p[1].type, p[3].type) != ""
            ):  # should be exactly equal or atleast one is a constant
                if notcomparable(p[1].type) or notcomparable(p[3].type):
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
                        type="BOOL",
                        children=[],
                    )
                    if p[1].type == "intconst" and p[3].type == "intconst":
                        p[0].val = operate(int(p[1].val), p[2], int(p[3].val))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].type = "boolconst"
                        p[0].ast = add_edges(p)
                    elif p[1].type == "floatconst" and p[3].type == "floatconst":
                        p[0].val = operate(float(p[1].val), p[2], float(p[3].val))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].type = "boolconst"
                        p[0].ast = add_edges(p)
                    else:
                        if p[3].type == "intconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "int" + p[2],
                                    p[0].place,
                                    p[1].place,
                                    p[3].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[3].type == "floatconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "float" + p[2],
                                    p[0].place,
                                    p[1].place,
                                    p[3].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type == "intconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "int" + p[2],
                                    p[0].place,
                                    p[3].place,
                                    p[1].place,
                                ]
                            )
                            p[0].ast = add_edges(p)

                        elif p[1].type == "floatconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "float" + p[2],
                                    p[0].place,
                                    p[3].place,
                                    p[1].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type in ["FLOAT32", "FLOAT64"]:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["float" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        else:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                    p[0].true = generate_label()
                    p[0].false = generate_label()
            else:
                print_compilation_error(
                    str(p[1].line_num)
                    + "COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
                    + " operator",
                )

        if p[2] == "<<" or p[2] == ">>":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    str(p[1].line_num)
                    + "COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
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
                if p[1].type == "intconst":
                    print_compilation_error(
                        str(p[1].line_num)
                        + "COMPILATION ERROR : Cannot apply"
                        + str(p[2])
                        + " with "
                        + str(p[1].type)
                    )

                else:
                    if p[3].type == "intconst":
                        p[0].code = p[1].code
                        p[0].place = get_token()
                        p[0].code.append(
                            [p[2] + "logical", p[0].place, p[1].place, p[3].place]
                        )
                        p[0].ast = add_edges(p)
                    else:
                        p[0].code = p[1].code
                        p[0].code = p[3].code
                        p[0].place = get_token()
                        p[0].code.append(
                            [p[2] + "variable", p[0].place, p[1].place, p[3].place]
                        )
                        p[0].ast = add_edges(p)
        if p[2] == "+" or p[2] == "-" or p[2] == "*":
            if (
                equal(p[1].type, p[3].type) != ""
            ):  # should be exactly equal or atleast one is a constant

                if notcomparable(p[1].type):
                    print_compilation_error(
                        str(p[1].line_num)
                        + "COMPILATION ERROR : Incomputable data type with "
                        + str(p[2])
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
                    if p[1].type == "intconst" and p[3].type == "intconst":
                        p[0].val = str(operate(int(p[1].val), p[2], int(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                    elif p[1].type == "floatconst" and p[3].type == "floatconst":
                        p[0].val = str(operate(float(p[1].val), p[2], float(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                    else:
                        if p[3].type == "intconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "int" + p[2],
                                    p[0].place,
                                    p[1].place,
                                    p[3].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[3].type == "floatconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "float" + p[2],
                                    p[0].place,
                                    p[1].place,
                                    p[3].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type == "intconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "int" + p[2],
                                    p[0].place,
                                    p[3].place,
                                    p[1].place,
                                ]
                            )
                            p[0].ast = add_edges(p)

                        elif p[1].type == "floatconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            p[0].code.append(
                                [
                                    "immediate" + "float" + p[2],
                                    p[0].place,
                                    p[3].place,
                                    p[1].place,
                                ]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type in ["FLOAT32", "FLOAT64"]:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code = p[1].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["float" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        else:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code = copy.deepcopy(p[1].code)
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    str(p[1].line_num)
                    + "COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
                    + " operator",
                )

        if p[2] == "/":
            if equal(p[1].type, p[3].type) != "":
                if notcomparable(p[1].type):
                    print_compilation_error(
                        str(p[1].line_num)
                        + "COMPILATION ERROR : Incomputable data type with "
                        + str(p[2])
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
                    if p[1].type == "intconst" and p[3].type == "intconst":
                        p[0].val = str((int(p[1].val) // int(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                    elif p[1].type == "floatconst" and p[3].type == "floatconst":
                        p[0].val = str((float(p[1].val) / float(p[3].val)))
                        p[0].code = []
                        p[0].place = p[0].val
                        p[0].ast = add_edges(p)
                        p[0].ast = add_edges(p)
                    else:
                        if p[3].type == "intconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            temp_token = get_token()
                            p[0].code.append(
                                ["load immediate ", temp_token, p[3].place]
                            )
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, temp_token]
                            )
                            p[0].ast = add_edges(p)
                        elif p[3].type == "floatconst":
                            p[0].code = p[1].code
                            p[0].place = get_token()
                            temp_token = get_token()
                            p[0].code.append(
                                ["load immediate ", temp_token, p[3].place]
                            )
                            p[0].code.append(
                                ["float" + p[2], p[0].place, p[1].place, temp_token]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type == "intconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            temp_token = get_token()
                            p[0].code.append(
                                ["load immediate ", temp_token, p[1].place]
                            )
                            p[0].code.append(
                                ["int" + p[2], p[0].place, temp_token, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        elif p[1].type == "floatconst":
                            p[0].code = p[3].code
                            p[0].place = get_token()
                            temp_token = get_token()
                            p[0].code.append(
                                ["load immediate ", temp_token, p[1].place]
                            )
                            p[0].code.append(
                                ["int" + p[2], p[0].place, temp_token, p[3].place]
                            )
                            p[0].ast = add_edges(p)

                        elif p[1].type in ["FLOAT32", "FLOAT64"]:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code = p[1].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["float" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        else:
                            p[0].code = p[1].code + p[3].code
                            # p[0].code = p[1].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
            else:
                print_compilation_error(
                    str(p[1].line_num)
                    + "COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
                    + " operator",
                )

        if p[2] == "%":
            if not (
                isint(p[1].type) and isint(p[3].type)
            ):  # can be int 8, int 32 etc or intconst
                print_compilation_error(
                    str(p[1].line_num)
                    + "COMPILATION ERROR : Incompatible data type with "
                    + str(p[2])
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
                    if p[1].type == "intconst" and p[3].type == "intconst":
                        p[0].val = str((int(p[1].val) % int(p[3].val)))
                        p[0].place = p[0].val
                        p[0].code = []
                        p[0].ast = add_edges(p)
                    else:
                        if p[1].type != "intconst" and p[3].type != "intconst":
                            p[0].code = p[1].code + p[3].code
                            # p[0].code = p[1].code
                            # p[0].code.append(p[3].code)
                            p[0].place = get_token()
                            p[0].code.append(
                                ["int" + p[2], p[0].place, p[1].place, p[3].place]
                            )
                            p[0].ast = add_edges(p)
                        else:
                            if p[1].type == "intconst":
                                p[0].code = p[3].code
                                p[0].place = get_token()
                                temp_token = get_token()
                                p[0].code.append(
                                    ["load immediate ", temp_token, p[1].place]
                                )
                                p[0].code.append(
                                    ["int" + p[2], p[0].place, temp_token, p[3].place]
                                )
                                p[0].ast = add_edges(p)
                            else:
                                p[0].code = p[1].code
                                p[0].place = get_token()
                                temp_token = get_token()
                                p[0].code.append(
                                    ["load immediate ", temp_token, p[3].place]
                                )
                                p[0].code.append(
                                    ["int" + p[2], p[0].place, p[1].place, temp_token]
                                )
                                p[0].ast = add_edges(p)
                else:
                    print_compilation_error(
                        str(p[1].line_num)
                        + "COMPILATION ERROR : Incompatible data type with "
                        + str(p[2])
                        + " operator",
                    )


def p_UnaryExpr(p):  #  handle 3AC of STAR , BIT_AND
    """UnaryExpr : PrimaryExpr
    | unary_op UnaryExpr"""

    if len(p) == 2:
        p[0] = p[1]
        p[0].code = p[1].code
        p[0].ast = add_edges(p)
    else:
        if (
            p[1].val == "&"
        ):  # to check on what what can it be applied -> composite literal for example
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
            p[0].place = get_token()
            p[0].code.append(["getaddress", p[0].place, p[2].place])

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
            p[0].place = get_token()
            p[0].code.append(["dereference", p[0].place, p[2].place])

        else:  # check on what this can be applied as well
            p[0] = Node(
                name="SimpleUnaryOperation",
                val=p[2].val,
                line_num=p[2].line_num,
                type=p[2].type,
                children=[p[2]],
            )
            p[0].ast = add_edges(p)
            if p[1].val == "-":
                if isint(p[2].type) or p[2].type in [
                    "FLOAT32",
                    "FLOAT64",
                    "floatconst",
                ]:
                    if p[2].type == "intconst":
                        p[0].val = str(-1 * int(p[2].val))
                        p[0].place = p[0].val
                    if p[1].type == "floatconst":
                        p[0].val = str(-1 * float(p[2].val))
                        p[0].place = p[0].val
                    if isint(p[2].type):
                        p[0].code = p[2].code
                        p[0].place = get_token()
                        p[0].code.append(
                            ["immediateint*", p[0].place, p[2].place, "-1"]
                        )
                    else:
                        p[0].code = p[2].code
                        p[0].place = get_token()
                        p[0].code.append(
                            ["immediatefloat*", p[0].place, p[2].place, "-1"]
                        )
                else:
                    print_compilation_error(
                        "COMPILATION ERROR at line "
                        + str(p[1].line_num)
                        + " cannot apply  operation of type "
                        + str(p[1].val)
                        + "to"
                        + str(p[2].type )
                    )

            if p[1].val == "+":
                if isint(p[2].type) or p[2].type in [
                    "FLOAT32",
                    "FLOAT64",
                    "floatconst",
                ]:
                    if p[2].type == "intconst":
                        p[0].val = str(int(p[2].val))
                    if p[1].type == "floatconst":
                        p[0].val = str(*float(p[2].val))
                else:
                    print_compilation_error(
                        "COMPILATION ERROR at line "
                        + str(p[1].line_num)
                        + " cannot apply  operation of type "
                        + str(p[1].val)
                        + "to"
                        + str(p[2].type)
                    )

            if p[1].val == "!":
                if p[2].type in ["boolconst"]:
                    if p[2].val == "True":
                        p[0].val = "False"
                    if p[2].val == "False":
                        p[0].val = "True"
                    p[0].place = p[0].val
                elif p[2].type == "BOOL":
                    p[0].place = get_token()
                    p[0].code = p[2].code
                    p[0].code.append([p[1], p[2].place, p[0].place])
                else:
                    print_compilation_error(
                        "COMPILATION ERROR at line "
                        + str(p[1].line_num)
                        + " cannot apply  operation of type "
                        + str(p[1].val)
                        + "to"
                        + str(p[2].type)
                    )


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
    global _global_sp
    global _current_scope
    global _current_size

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
            + str(lexeme)
            + " already declared "
        )

    p[0] = Node(name="VarSpec", val="", type="", line_num=p.lineno(1), children=[])
    p[0].ast = add_edges(p)

    if not p[3].type.startswith("ARRAY"):
        p[0].code = p[3].code
        if p[3].type.endswith("*") or p[3].type in [
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
            "BOOL",
        ]:
            p[0].code.append(["int_copy", lexeme, p[3].place])
        elif p[3].type in ["FLOAT32", "FLOAT64"]:
            p[0].code.append(["float_copy", lexeme, p[3].place])
        elif p[3].type in ["STRING"]:
            p[0].code.append(["string_copy", lexeme, p[3].place])
        elif p[3].type == "intconst":
            p[0].code.append(["int_copy_immediate", lexeme, p[3].place])
        elif p[3].type == "floatconst":
            p[0].code.append(["float_copy_immediate", lexeme, p[3].place])
        elif p[3].type == "boolconst":
            if p[3].place == "True":
                p[0].code.append(["load immediate", lexeme, "1"])
            else:
                p[0].code.append(["load immediate", lexeme, "0"])
        elif p[3].type == "stringconst":
            p[0].code.append(["string_copy_immediate", lexeme, p[3].place])

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
            if p[3].type.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += 8
                _global_sp += 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = _size[p[3].type]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += _size[p[3].type]
                _global_sp += _size[p[3].type]

        else:
            i = 0
            SYMBOL_TABLE[_current_scope][lexeme] = {}
            SYMBOL_TABLE[_current_scope][lexeme]["type"] = p[3].type
            temp = p[3].type.split()
            dim = []
            Quant = 1
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                Quant *= int(temp[i])
                i = i + 1
            typ = temp[i]
            if typ == "struct":
                typ = typ + " " + temp[i + 1]
            if typ.endswith("*"):
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * 8
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * 8
                _global_sp += Quant * 8
            else:
                SYMBOL_TABLE[_current_scope][lexeme]["size"] = Quant * _size[typ]
                SYMBOL_TABLE[_current_scope][lexeme]["offset"] = _global_sp
                _current_size[_current_scope] += Quant * _size[typ]
                _global_sp += Quant * _size[typ]
            SYMBOL_TABLE[_current_scope][lexeme]["array"] = dim


# Function Declaration


def p_func_decl(p):
    """FunctionDecl : funcBegin FunctionName Signature  FunctionBody"""
    p[0] = Node(name="FunctionDecl", val="", type="", children=[], line_num=p.lineno(1))

    # arg_list = []
    # for i in p[3].children:
    #     arg_list.append(i.type)
    p[0].ast = add_edges(p)

    global _current_scope
    global _current_size
    global _global_sp

    _global_sp -= _current_size[_current_scope]
    _current_scope = _parent[_current_scope]

    p[0].code = p[4].code

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
    global _current_size
    global _global_sp

    _global_sp = 0

    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    _current_size[_current_scope] = 0
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
            + str(lexeme)
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
    p[0].code = p[1].code


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
        SYMBOL_TABLE[_current_scope][child.val]["size"] = _size.get(child.type, 0)
        if child.type.endswith("*"):
            SYMBOL_TABLE[_current_scope][child.val]["size"] = 8
        else:
            SYMBOL_TABLE[_current_scope][child.val]["size"] = _size.get(child.type, 0)
        arg_list.append(child.type)

        if child.type.startswith("ARRAY"):
            i = 0
            temp = child.type.split()
            dim = []
            Quant = 1
            while temp[i] == "ARRAY":
                i = i + 1
                dim.append(int(temp[i]))
                Quant *= int(temp[i])
                i = i + 1
            typ = temp[i]
            if typ == "struct":
                typ = typ + " " + temp[i + 1]
            if typ.endswith("*"):
                SYMBOL_TABLE[_current_scope][child.val]["size"] = Quant * 8
            else:
                SYMBOL_TABLE[_current_scope][child.val]["size"] = Quant * _size[typ]
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


def p_IfStmt_1(p):
    """IfStmt : IFBegin SimpleStmt SEMICOLON Expression Block
    | IFBegin SimpleStmt SEMICOLON Expression Block ELSE Block
    | IFBegin Expression Block
    """
    p[0] = Node(name="IfStmt", val="", type="", children=[], line_num=p.lineno(1))

    global _global_sp
    global _current_scope
    global _parent

    _global_sp -= _current_size[_current_scope] 
    _current_scope = _parent[_current_scope]
    p[0].ast = add_edges(p)

    ## can apply type chek if required
    exit_label = generate_label()

    if len(p) == 4:
        p[0].code = p[2].code
        newlabel = p[2].false  # to be implemented
        p[0].code.append(["if", p[2].place, "==", "False", "goto", newlabel])
        p[0].code.append([p[2].true])
        p[0].code += p[3].code
        p[0].code.append(["goto", exit_label])
        p[0].code.append([newlabel])
        p[0].code.append([exit_label])

    elif len(p) == 6:
        p[0].code = p[2].code
        p[0].code += p[4].code
        newlabel = p[4].false  # to be implemented
        p[0].code.append(["if", p[4].place, "==", "False", "goto", newlabel])
        p[0].code.append([p[4].true])
        p[0].code += p[5].code
        p[0].code.append(["goto", exit_label])
        p[0].code.append([newlabel])
        p[0].code.append([exit_label])

    elif len(p) == 8:
        p[0].code = p[2].code
        p[0].code += p[4].code
        newlabel = p[4].false  # to be implemented
        p[0].code.append(["if", p[4].place, "==", "False", "goto", newlabel])
        p[0].code.append([p[4].true])
        p[0].code += p[5].code
        newlabel1 = generate_label()
        p[0].code.append(["goto", newlabel1])
        p[0].code.append([newlabel])
        p[0].code += p[5].code
        p[0].code.append([newlabel1])


def p_IfStmt_2(p):
    """IfStmt : IFBegin SimpleStmt SEMICOLON Expression Block ELSE IfStmt
    | IFBegin Expression Block ELSE  Block
    """
    p[0] = Node(name="IfStmt", val="", type="", children=[], line_num=p.lineno(1))

    global _global_sp
    global _current_scope

    _global_sp -= _current_size[_current_scope] 
    _current_scope = _parent[_current_scope]
    p[0].ast = add_edges(p)

    ## can apply type check if required

    if len(p) == 6:
        p[0].code = p[2].code
        newlabel = p[2].false  # to be implemented
        p[0].code.append(["if", p[2].place, "==", "False", "goto", newlabel])

        p[0].code.append([p[2].true])
        p[0].code += p[3].code
        newlabel1 = generate_label()
        p[0].code.append(["goto", newlabel1])
        p[0].code.append([newlabel])
        p[0].code += p[5].code
        p[0].code.append([newlabel1])

    else:
        p[0].code = p[2].code
        p[0].code += p[4].code
        newlabel = p[4].false  # to be implemented
        p[0].code.append(["if", p[4].place, "==", "False", "goto", newlabel])
        p[0].code.append([p[4].true])
        p[0].code += p[5].code
        newlabel1 = generate_label()
        p[0].code.append(["goto", newlabel1])
        p[0].code.append([newlabel])
        p[0].code += p[5].code
        p[0].code.append([newlabel1])


def p_IfStmt_3(p):
    """IfStmt : IFBegin Expression Block ELSE  IfStmt"""
    p[0] = Node(name="IfStmt", val="", type="", children=[], line_num=p.lineno(1))

    global _global_sp
    global _current_scope

    _global_sp -= _current_size[_current_scope]
    _current_scope = _parent[_current_scope]
    p[0].ast = add_edges(p)

    ## can apply type chek if required
    p[0].code = p[2].code
    newlabel = p[2].false  # to be implemented
    p[0].code.append(["if", p[2].place, "==", "False", "goto", newlabel])

    p[0].code.append([p[2].true])
    p[0].code += p[3].code
    newlabel1 = generate_label()
    p[0].code.append(["goto", newlabel1])
    p[0].code.append([newlabel])
    p[0].code += p[5].code
    p[0].code.append([newlabel1])


# def p_IfStmt(p):
#     """IfStmt : IFBegin SimpleStmt SEMICOLON Expression Block
#     | IFBegin SimpleStmt SEMICOLON Expression Block ELSE Block
#     | IFBegin SimpleStmt SEMICOLON Expression Block ELSE IfStmt
#     | IFBegin Expression Block
#     | IFBegin Expression Block ELSE  IfStmt
#     | IFBegin Expression Block ELSE  Block
#     """
#     p[0] = Node(name="IfStmt", val="", type="", children=[], line_num=p.lineno(1))
#     global _current_scope
#     _current_scope = _parent[_current_scope]
#     p[0].ast = add_edges(p)


def p_IfBegin(p):
    """IFBegin : IF"""
    global _current_scope
    global _next_scope
    global _current_scope

    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    _current_size[_current_scope] = 0

    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1
    p[0] = p[1]
    p[0] = add_edges(p)


def p_SwitchStmt(p):
    """SwitchStmt : SWITCH ExpressionSwitch LEFT_BRACE expr_case_clause_list RIGHT_BRACE
    | SWITCH LEFT_BRACE  expr_case_clause_list RIGHT_BRACE
    """
    p[0] = Node(name="SwitchStmt", val="", type="", children=[], line_num=p.lineno(1))

    global _exit_label_switch

    # check if all the type match with the type of expression added in switch
    if len(p) == 6:
        if p[4] is not None:
            for child in p[4].children:
                if child.type != "default" and equal(p[2].type, child.type) == "":
                    print_compilation_error(
                        "COMPILATION ERROR at line "
                        + str(child.line_num)
                        + ", Expression type: "
                        + str(p[2].type)
                        + "doesn't match with Case type:"
                        + str(child.type)
                    )

            p[0].code = p[2].code + p[4].code
            p[0].code.append([_exit_label_switch])

    p[0].ast = add_edges(p)


def p_ExpressionSwitch(p):
    """ExpressionSwitch : Expression"""
    p[0] = p[1]
    p[0].ast = add_edges(p)
    global _current_switch_place
    global _exit_label_switch

    _current_switch_place = p[1].place
    _exit_label_switch = generate_label()


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
        p[0].code = p[1].code + p[3].code

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
        p[0].code = p[1].code


##TODO why do we have a expression list here , doesn't work in go but is there in the doc
## Expression list external dependency
def p_ExprSwitchCase(p):
    """ExprSwitchCase : CASE ExpressionList
    | DEFAULT
    """
    global _current_scope
    global _next_scope
    global _current_size

    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    _current_size[_current_scope] = 0

    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1

    if len(p) == 3:
        p[0] = Node(
            name="ExprSwitchCase", val="", type="", children=[], line_num=p.lineno(1)
        )
        check = True
        i = 0
        p[0].placelist = []
        p[0].code = p[2].code
        for i in range(len(p[2].children)):
            if p[2].children[i].type != p[2].children[0].type:
                check = False
            p[0].placelist.append(p[2].children[i].place)

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
    global _current_switch_place
    global _exit_label_switch

    newlabel = generate_label()
    newlabel1 = generate_label()
    p[0].code = p[1].code

    if p[1].type == "default":
        p[0].code.append(["goto", newlabel])
    else:
        for i in p[1].placelist:
            p[0].code.append(["if", _current_switch_place, "==", i, "goto", newlabel])

    p[0].code.append(["goto", newlabel1])
    p[0].code.append([newlabel])
    p[0].code += p[3].code
    p[0].code.append(["goto", _exit_label_switch])
    p[0].code.append([newlabel1])

    p[0].type = p[1].type
    p[0].ast = add_edges(p)

    global _current_scope
    global _current_size
    global _global_sp

    _global_sp -= _current_size[_current_scope]
    _current_scope = _parent[_current_scope]


def p_ForStmt_1(p):
    """ForStmt : ForBegin Block
    | ForBegin Expression Block
    """
    p[0] = Node(name="ForStmt", val="", type="", children=[], line_num=p.lineno(1))

    global _current_scope
    global _current_size
    global _global_sp

    _global_sp -= _current_size[_current_scope]
    _current_scope = _parent[_current_scope]
    p[0].ast = add_edges(p)

    global _break_label
    global _continue_label
    global _loop_depth
    p[0].code = [[_continue_label[_loop_depth]]]

    ## TODO of the expression doesn't evaluate a true or false value then it wont work
    if len(p) == 3:
        p[0].code += p[2].code
        p[0].code.append(["goto", _continue_label[_loop_depth]])
        p[0].code.append([_break_label[_loop_depth]])

    ## TODO what would be it be "False" || "FALSE" || "false"
    else:
        p[0].code += p[1].code
        p[0].code.append(
            ["if", p[2].place, "==", "False", "goto", _break_label[_loop_depth]]
        )
        p[0].code += p[2].code
        p[0].code.append(["goto", _continue_label[_loop_depth]])
        p[0].code.append([_break_label[_loop_depth]])

    _loop_depth -= 1


def p_ForStmt_2(p):
    """ForStmt : ForBegin ForClause Block"""
    p[0] = Node(name="ForStmt", val="", type="", children=[], line_num=p.lineno(1))
    global _loop_depth
    global _current_scope
    global _break_label
    global _continue_label
    global _current_size
    global _global_sp

    _global_sp -= _current_size[_current_scope]
    _current_scope = _parent[_current_scope]
    p[0].ast = add_edges(p)

    p[0].code = p[2].code
    p[0].code += p[3].code

    if len(p[2].update) != 0:
        p[0].code += p[2].update

    p[0].code.append(["goto", _continue_label[_loop_depth]])
    p[0].code.append([_break_label[_loop_depth]])

    _loop_depth -= 1


# def p_ForStmt(p):
#     """ForStmt : ForBegin Block
#     | ForBegin Expression Block
#     | ForBegin ForClause Block
#     """
#     p[0] = Node(name="ForStmt", val="", type="", children=[], line_num=p.lineno(1))
#     global _loop_depth
#     _loop_depth -= 1
#     global _current_scope
#     _current_scope = _parent[_current_scope]
#     p[0].ast = add_edges(p)


def p_ForBegin(p):
    """ForBegin : FOR"""
    global _loop_depth
    _loop_depth += 1
    global _current_scope
    global _next_scope
    global _continue_label
    global _break_label
    global _current_size

    _parent[_next_scope] = _current_scope
    _current_scope = _next_scope
    _current_size[_current_scope] = 0

    SYMBOL_TABLE.append({})
    _next_scope = _next_scope + 1
    p[0] = p[1]
    p[0] = add_edges(p)

    newlabel = generate_label()
    newlabel1 = generate_label()

    _continue_label[_loop_depth] = newlabel
    _break_label[_loop_depth] = newlabel1


# TODO scope size -= for each end scope of for if
def p_ForClause_1(p):
    """ForClause :  SimpleStmt SEMICOLON Expression SEMICOLON SimpleStmt
    | SimpleStmt SEMICOLON             SEMICOLON SimpleStmt
    | SimpleStmt SEMICOLON             SEMICOLON
    |            SEMICOLON             SEMICOLON
    """
    if(type(p) is Node):
        line_num = max(p[1].line_num, p.lineno(1))
    else:
        line_num = p.lineno(1)
    p[0] = Node(
        name="ForClause", val="", type="", children=[], line_num=line_num, update=[]
    )
    p[0].ast = add_edges(p)

    global _loop_depth
    global _break_label
    global _continue_label

    if len(p) == 3:
        p[0].code = [[_continue_label[_loop_depth]]]

    else:
        p[0].code = p[1].code
        p[0].code.append([_continue_label[_loop_depth]])

        if len(p) == 6:
            p[0].code += p[3].code
            # p[0].code.append(p[3].code)
            p[0].code.append(
                ["if", p[3].place, "==", "False", "goto", _break_label[_loop_depth]]
            )
            # TODO update instruction add to node
            p[0].update = p[5].code

        elif len(p) == 5:
            p[0].update = p[4].code


def p_ForClause_2(p):
    """ForClause :             SEMICOLON             SEMICOLON SimpleStmt
    | SimpleStmt SEMICOLON  Expression SEMICOLON
    """
    if(type(p) is Node):
        line_num = max(p[1].line_num, p.lineno(1))
    else:
        line_num = p.lineno(1)
    p[0] = Node(
        name="ForClause", val="", type="", children=[], line_num=line_num, update=[]
    )
    p[0].ast = add_edges(p)

    global _loop_depth
    global _break_label
    global _continue_label

    if len(p) == 4:
        p[0].code.append([_continue_label[_loop_depth]])
        p[0].update = p[3].code
    else:
        p[0].code = p[1].code + p[3].code
        p[0].code.append([_continue_label[_loop_depth]])
        # p[0].code.append(p[3].code)
        p[0].code.append(
            ["if", p[3].place, "==", "False", "goto", _break_label[_loop_depth]]
        )


def p_ForClause_3(p):
    """ForClause :            SEMICOLON  Expression SEMICOLON SimpleStmt
    |            SEMICOLON  Expression SEMICOLON
    """
    if(type(p) is Node):
        line_num = max(p[1].line_num, p.lineno(1))
    else:
        line_num = p.lineno(1)
    p[0] = Node(
        name="ForClause", val="", type="", children=[], line_num=line_num, update=[]
    )
    p[0].ast = add_edges(p)

    global _loop_depth
    global _break_label
    global _continue_label

    if len(p) == 4:
        p[0].code.append([_continue_label[_loop_depth]])
        p[0].code += p[2].code
        p[0].code.append(
            ["if", p[2].place, "==", "False", "goto", _break_label[_loop_depth]]
        )

    else:
        p[0].code.append([_continue_label[_loop_depth]])
        p[0].code += p[2].code
        p[0].code.append(
            ["if", p[2].place, "==", "False", "goto", _break_label[_loop_depth]]
        )
        p[0].update = p[4].code


# def p_ForClause(p):
#     """ForClause :  SimpleStmt SEMICOLON Expression SEMICOLON SimpleStmt
#     | SimpleStmt SEMICOLON             SEMICOLON SimpleStmt
#     | SimpleStmt SEMICOLON             SEMICOLON
#     |            SEMICOLON             SEMICOLON SimpleStmt
#     | SimpleStmt SEMICOLON  Expression SEMICOLON
#     |            SEMICOLON  Expression SEMICOLON SimpleStmt
#     |            SEMICOLON  Expression SEMICOLON
#     |            SEMICOLON             SEMICOLON
#     """
#     line_num = max(p[1].line_num, p.lineno(1))
#     p[0] = Node(name="ForClause", val="", type="", children=[], line_num=line_num)
#     p[0].ast = add_edges(p)


def p_error(p):
    if p:
        print_compilation_error(
            "Syntax error at token " + str(p.type) + "  Line Number  " + str(p.lineno)
        )
        # Just discard the token and tell the parser it's okay.
        # parser.errok()
    else:
        print_compilation_error("Syntax error at EOF")


def dump_symbol_table():
    global _symbol_table_dump_filename

    with open(_symbol_table_dump_filename, "w") as f:
        f.write(
            "Scope, Name, Size, Offset, Val, Line Num, Type, Children, Array, Function, Level, Field List\n"
        )

    for i in range(_next_scope):
        if len(SYMBOL_TABLE[i]) > 0:
            temp_list = {}
            for key in SYMBOL_TABLE[i].keys():
                temp_list[key] = SYMBOL_TABLE[i][key]

            with open(_symbol_table_dump_filename, "a") as f:
                for j in range(len(temp_list)):
                    values = list(temp_list.values())[j]

                    keys = list(temp_list.keys())[j]

                    f.write(
                        f'{i}, {keys}, {values.get("size", "")}, {values.get("offset", "")}, {values.get("val", "")}, {values.get("line_num", "")}, {values.get("type", "")}, {values.get("children", "")}, {values.get("array", "")}, {values.get("func", "")}, {values.get("level", "")}, {values.get("field_list", "")}\n'
                    )


parser = yacc.yacc()


def main():
    # try:
    global _3ac_code
    global _symbol_table_dump_filename
    global _ast_filename
    global _ast_plot_filename
    global _ircode_filename

    argparser = argparse.ArgumentParser(
        description="A parser for the source language that outputs the Parser Automaton in a graphical form."
    )
    argparser.add_argument("filepath", type=str, help="Path for your go program")
    args = argparser.parse_args()

    go_filename = os.path.basename(args.filepath)
    if "." in go_filename:
        go_filename = go_filename.split(".")[0]

    _symbol_table_dump_filename = SYMBOL_TABLE_DUMP_FILENAME.format(go_filename)
    _ast_filename = AST_FILENAME.format(go_filename)
    _ast_plot_filename = AST_PLOT_FILENAME.format(go_filename)
    _ircode_filename = IRCODE_FILENAME.format(go_filename)

    with open(args.filepath) as f:
        program = f.read().rstrip() + "\n"

    print("> Parser initiated")

    print("> AST dotfile generation initiated")

    with open(_ast_filename, "w") as f:
        f.write("digraph G {")

    parser = yacc.yacc()
    parser.parse(program)

    print("> Parser ended")

    with open(_ast_filename, "a") as f:
        f.write("\n}")

    print("> AST dotfile generation ended")

    print_success("> SYMBOL TABLE:")
    pprint(SYMBOL_TABLE)

    print_success("> 3AC Code")
    pprint(_3ac_code)

    graphs = pydot.graph_from_dot_file(_ast_filename)
    graph = graphs[0]
    graph.write_png(_ast_plot_filename)

    dump_symbol_table()

    write_ircode(_ircode_filename, _3ac_code)

    print(
        f"> Dump of the Symbol Table has been saved as '{_symbol_table_dump_filename}'"
    )
    print(f"> Dump of the AST has been saved as '{_ast_filename}'")
    print(f"> Dump of the AST has been plotted in '{_ast_plot_filename}'")
    print(f"> 3AC code has been saved in '{_ircode_filename}'")

    print_success("Semantic Analysis done successfully")

    return 0

    # except Exception as e:
    print_failure(e)


# return -1


if __name__ == "__main__":
    sys.exit(main())
