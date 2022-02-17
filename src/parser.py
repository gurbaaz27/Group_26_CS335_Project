##########################
## Milestone 3 : CS335A ##
########################################
## Submission Date: February 18, 2022 ##
########################################

__author__ = "Group 26, CS335A"
__filename__ = "parser.py"
__description__ = "A parser for the source language that outputs the Parser Automaton in a graphical form."

import argparse
import ply.yacc as yacc
from lexer import lexer
from dot import generate_LR_automata


def p_start(p):
    """start: Sourcefile"""


def p_empty(p):
    """empty:"""


###############
##### EOS #####
###############


def p_EOS(p):
    """EOS: NEWLINE
    | SEMICOLON
    """


#################
##### TYPE #####
#################


def p_TypeName(p):
    """TypeName: UINT
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
    | IDENTIFIER
    """


def p_TypeLit(p):
    """TypeLit: StructType
    | ArrayType
    | Slicetype
    | PointerType
    """


def p_Type(p):
    """Type: TypeName
    | TypeLit
    | LEFT_PARENTH Type RIGHT_PARENTH
    """


#################
##### ARRAY #####
#################


def p_ArrayType(p):
    """ArrayType: LEFT_SQUARE ArrayLength RIGHT_SQUARE ElementType"""


def p_ArrayLength(p):
    """ArrayLength: Expression"""


def p_ElementType(p):
    """ElementType: Type"""


#################
##### SLICE #####
#################


def p_SliceType(p):
    """SliceType: LEFT_SQUARE RIGHT_SQUARE ElementType"""


##################
##### STRUCT #####
##################


def p_StructType(p):
    """StructType: STRUCT LEFT_BRACE Fields RIGHT_BRACE"""


def p_Fields(p):
    """Fields: FieldDecl EOS
    | FieldDecl EOS Fields"""


def p_FieldDecl(p):
    """FieldDecl: IDENTIFIER Type"""


#############
## POINTER ##
#############
def p_PointerType(p):
    """PointerType: STAR Type"""


def p_Block(p):
    """Block: LEFT_BRACE StatementList RIGHT_BRACE"""


def p_StatementList(p):
    """StatementList: Statement EOS StatementList"""


###############
## STATEMENT ##
###############
def p_Statement(p):
    """Statement: Declaration
    | SimpleStmt
    | ReturnStmt
    | BreakStmt
    | ContinueStmt
    | Block
    | IfStmt
    | SwitchStmt
    | ForStmt"""


## RETURN STATEMENT
def p_ReturnStmt(p):
    """ReturnStmt: RETURN Expression
    | RETURN"""


## BREAK STATEMENT
def p_BreakStmt(p):
    """BreakStmt: BREAK Expression
    | BREAK"""


## CONTINUE STATEMENT
def p_ContinueStmt(p):
    """ContinueStmt: CONTINUE"""


## DECLARATION
def p_Declaration(p):
    """Declaration: ConstDecl
    | VarDecl"""


## 1. ConstDecl
def p_ConstDecl(p):
    """ConstDecl: CONST ConstSpec"""


def p_ConstSpec(p):
    """ConstSpec: Identifier Type ASSIGN Expression
    | Identifier ASSIGN Expression"""


## 2. Typedecl
def p_TypeDecl(p):
    """TypeDecl: TYPE TypeSpec"""


def p_TypeSpec(p):
    """TypeSpec: AliasDecl
    | Typedef"""


def p_AliasDecl(p):
    """AliasDecl: IDENTIFIER ASSIGN Type"""


def p_TypeDef(p):
    """TypeDef: IDENTIFIER Type"""


## 3. VarDecl
def p_VarDecl(p):
    """VarDecl: VAR VarSpec"""


## VarSpec
def p_VarSpec(p):
    """VarSpec: IDENTIFIER"""


## SIMPLE STATEMENT
def p_SimpleStmt(p):
    """SimpleStmt: EmptyStmt
    | ExpressionStmt
    | IncDecStmt
    | Assignment
    | ShortVarDecl"""


# 1.
def p_EmptyStmt(p):
    """EmptyStmt: empty"""


# 2.
def p_ExpressionStmt(p):
    """ExpressionStmt: Expression"""


# 3.
def p_IncDecStmt(p):
    """IncDecStmt: Expression INCREMENT
    | Expression DECREMENT"""


# 4.
def p_Assignment(p):
    """Assignment: Expression assign_op Expression"""


### COVER ALL HERE
def p_assign_op(p):
    """assign_op: RIGHT_SHIFT_EQUAL
    | LEFT_SHIFT_EQUAL
    | PLUS_ASSIGN
    | MINUS_ASSIGN
    | STAR_ASSIGN
    | DIV_ASSIGN
    | MOD_ASSIGN
    | AND_ASSIGN
    | OR_ASSIGN
    | XOR_ASSIGN"""


### Expression
def p_Expression(p):
    """Expression:  = UnaryExpr
    | Expression binary_op Expression"""


def p_binary_op(p):
    """binary_op: OR
    | AND
    | rel_op
    | add_op
    | mul_op"""


def p_rel_op(p):
    """rel_op: EQUAL
    | NOT_EQUAL
    | LESS
    | GREATER
    | LESS_EQUAL
    | GREATER_EQUAL"""


def p_add_mul_op(p):
    """add_mul_op: add_op
    | mul_op"""


def p_add_op(p):
    """add_op: PLUS
    | MINUS
    | BIT_OR
    | BIT_XOR"""


def p_mul_op(p):
    """mul_op: STAR
    | DIV
    | MOD
    | LEFT_SHIFT
    | RIGHT_SHIFT
    | BIT_AND"""


# 5.
def p_ShortVarDecl(p):
    """ShortVarDecl: Identifier COLON_ASSIGN Expression"""


# Function Declaration
def p_func_decl(p):
    """FunctionDecl : FUNC FunctionName Signature  FunctionBody
     FunctionName : identifier
     FunctionBody : Block
     Signature    : Parameters Result
                  | Parameters
     Result       :  Type
    Parameters    : LEFT_PARENTH RIGHT_PARENTH
                  | LEFT_PARENTH ParameterList RIGHT_PARENTH
    ParameterList  : ParameterDecl COMMA ParameterList
                   | ParameterDecl
    ParameterDecl  : identifier Type"""


################################################################
# my task
###############################################
## ehde ch doubt eh aa ki group karke ghta skde aa ke ni - specifically else ton baad aala part
def p_IfStmt(p):
    """IfStmt: IF SimpleStmt SEMICOLON Expression Block
    | IF SimpleStmt SEMICOLON Expression Block ELSE Block
    | IF SimpleStmt SEMICOLON Expression Block ELSE IfStmt
    | IF Expression Block
    | IF Expression Block ELSE  IfStmt
    | IF Expression Block ELSE  Block
    """


###############################################
## type switch statement ni rakhiya
def p_SwitchStmt(p):
    """SwitchStmt: SWITCH  SimpleStmt SEMICOLON Expression LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH
    | SWITCH                       Expression LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH
    | SWITCH  SimpleStmt SEMICOLON            LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH
    | SWITCH                                  LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH
    """


## hun ehde ch exprecasecluase kaafi ho skde c switch stmt - {} nal denote kita c and in BNF i have written it like this
## check the empty one
###custom made so check karna
def p_expr_case_clause_list(p):
    """expr_case_clause_list: ExprCaseClause Eos expr_case_clause_list
    | empty
    """


## expression list external dependency
def ExprSwitchCase(p):
    """ExprSwitchCase: CASE ExpressionList
    | DEFAULT
    """


## statement list external dependency
def p_ExprCaseClause(p):
    """ExprCaseClause: ExprSwitchCase COLON StatementList"""


###############################################
def p_ForStmt(p):
    """ForStmt: FOR Block
    | FOR Expression Block
    | FOR ForClause Block
    """


## i feel like all these repetitive cases can be avoided just by using empty in expression or statement
def p_ForClause(p):
    """ForClause:  SimpleStmt SEMICOLON Expression SEMICOLON SimpleStmt
    | SimpleStmt SEMICOLON            SEMICOLON SimpleStmt
    """

parser = yacc.yacc()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="A parser for the source language that outputs the Parser Automaton in a graphical form."
    )
    parser.add_argument("filepath", type=str, help="Path for your go program")
    args = parser.parse_args()

    with open(args.filepath) as f:
        program = f.read()

    lexer.input(program)

    result = parser.parse(program)

    generate_LR_automata(result)
