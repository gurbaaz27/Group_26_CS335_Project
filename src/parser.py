##########################
## Milestone 3  : CS335A ##
########################################
## Submission Date : February 18, 2022 ##
########################################

__author__ = "Group 26, CS335A"
__filename__ = "parser.py"
__description__ = "A parser for the source language that outputs the Parser Automaton in a graphical form."

import argparse
import ply.yacc as yacc
from lexer import tokens

# from dot import generate_LR_automata


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
    ("left",  "RIGHT_PARENTH", "LEFT_PARENTH", "LEFT_BRACE", "RIGHT_BRACE", "LEFT_SQUARE", "RIGHT_SQUARE", "INCREMENT", "DECREMENT"),
)


def p_start(p) :
    """start : SourceFile"""

def p_empty(p):
    """empty :"""


###############
##### EOS #####
###############


def p_EOS(p):
    """EOS : SEMICOLON """


#################
##### TYPE #####
#################


def p_TypeName(p):
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
    | IDENTIFIER
    """


def p_TypeLit(p):
    """TypeLit : StructType
    | ArrayType
    | SliceType
    | PointerType
    """


def p_Type(p):
    """Type : TypeName
    | TypeLit
    | LEFT_PARENTH Type RIGHT_PARENTH
    """


#################
##### ARRAY #####
#################


def p_ArrayType(p):
    """ArrayType : LEFT_SQUARE ArrayLength RIGHT_SQUARE ElementType"""


def p_ArrayLength(p):
    """ArrayLength : Expression"""


def p_ElementType(p):
    """ElementType : Type"""


#################
##### SLICE #####
#################


def p_SliceType(p):
    """SliceType : LEFT_SQUARE RIGHT_SQUARE ElementType"""


##################
##### STRUCT #####
##################


def p_StructType(p):
    """StructType : STRUCT LEFT_BRACE Fields RIGHT_BRACE"""


def p_Fields(p):
    """Fields : FieldDecl EOS
    | FieldDecl EOS Fields"""


def p_FieldDecl(p):
    """FieldDecl : IDENTIFIER Type"""


#############
## POINTER ##
#############
def p_PointerType(p):
    """PointerType : STAR Type"""


###########
## BLOCK ##
###########


def p_Block(p):
    """Block : LEFT_BRACE StatementList RIGHT_BRACE"""


def p_StatementList(p):
    """StatementList : Statement EOS StatementList
    | EOS StatementList
    | empty"""


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


## RETURN STATEMENT
def p_ReturnStmt(p):
    """ReturnStmt : RETURN Expression
    | RETURN"""


## BREAK STATEMENT
def p_BreakStmt(p):
    """BreakStmt : BREAK Expression
    | BREAK"""


## CONTINUE STATEMENT
def p_ContinueStmt(p):
    """ContinueStmt : CONTINUE"""


## DECLARATION
def p_Declaration(p):
    """Declaration : ConstDecl
    | TypeDecl
    | VarDecl"""


def p_TopLevelDecl(p):
    """TopLevelDecl : Declaration
    | FunctionDecl"""

def p_TopLevelDeclList(p):
    """TopLevelDeclList : TopLevelDecl EOS TopLevelDeclList 
    | empty"""


def p_SourceFile(p):
    """SourceFile : TopLevelDeclList"""


## 1. ConstDecl
def p_ConstDecl(p):
    """ConstDecl : CONST ConstSpec"""


def p_ConstSpec(p):
    """ConstSpec : IDENTIFIER Type ASSIGN Expression
    | IDENTIFIER ASSIGN Expression"""


## 2. Typedecl
def p_TypeDecl(p):
    """TypeDecl : TYPE TypeSpec"""


def p_TypeSpec(p):
    """TypeSpec : AliasDecl
    | TypeDef"""


def p_AliasDecl(p):
    """AliasDecl : IDENTIFIER ASSIGN Type"""


def p_TypeDef(p):
    """TypeDef : IDENTIFIER Type"""


## 3. VarDecl
def p_VarDecl(p):
    """VarDecl : VAR VarSpec"""


## VarSpec
def p_VarSpec(p):
    """VarSpec : IDENTIFIER Type ASSIGN Expression
    | IDENTIFIER ASSIGN Expression
    | IDENTIFIER Type"""


## SIMPLE STATEMENT
def p_SimpleStmt(p):
    """SimpleStmt : EmptyStmt
    | ExpressionStmt
    | IncDecStmt
    | Assignment
    | ShortVarDecl"""


# 1.
def p_EmptyStmt(p):
    """EmptyStmt : empty"""


# 2.
def p_ExpressionStmt(p):
    """ExpressionStmt : Expression"""


# 3.
def p_IncDecStmt(p):
    """IncDecStmt : Expression INCREMENT
    | Expression DECREMENT"""


# 4.
def p_Assignment(p):
    """Assignment : Expression assign_op Expression"""


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


## ExpressionList
def p_ExpressionList(p):
    """
    ExpressionList  :  Expression COMMA ExpressionList
                    | Expression
    """


## Primary Expression
def p_PrimaryExpr(p):
    """
    PrimaryExpr  : Operand
                | PrimaryExpr Selector
                | PrimaryExpr Index
                | PrimaryExpr Slice
                | PrimaryExpr Arguments

    Selector     : DOT IDENTIFIER
    Index        :  LEFT_SQUARE Expression RIGHT_SQUARE
    Slice        :  LEFT_SQUARE Expression  COLON Expression  RIGHT_SQUARE
                |  LEFT_SQUARE  COLON  Expression  RIGHT_SQUARE
                |  LEFT_SQUARE  Expression  COLON  RIGHT_SQUARE
                |  LEFT_SQUARE COLON RIGHT_SQUARE

    Arguments   :  LEFT_PARENTH RIGHT_PARENTH
                |  LEFT_PARENTH ExpressionList RIGHT_PARENTH
                | LEFT_PARENTH Type RIGHT_PARENTH
                | LEFT_PARENTH Type COMMA ExpressionList RIGHT_PARENTH
    """


def p_Operand(p):
    """Operand : Literal
    | OperandName
    | LEFT_PARENTH Expression RIGHT_PARENTH"""


def p_Literal(p):
    """Literal : BasicLit
    | CompositeLit
    | FunctionLit"""


def p_FunctionLit(p):
    """FunctionLit : FUNC Signature FunctionBody"""


def p_BasicLit(p):
    """BasicLit : INTCONST
    | FLOATCONST
    | STRINGCONST
    | BOOLCONST"""


def p_OperandName(p):
    """OperandName : IDENTIFIER"""


def p_CompositeLit(p):
    """CompositeLit : LiteralType LiteralValue"""


def p_LiteralType(p):
    """LiteralType : StructType
    | ArrayType
    | SliceType
    | IDENTIFIER"""


def p_LiteralValue(p):
    """LiteralValue : LEFT_BRACE ElementList RIGHT_BRACE
    | LEFT_BRACE RIGHT_BRACE"""


def p_ElementList(p):
    """ElementList : Element COMMA ElementList
    | Element"""


def p_Element(p):
    """Element : Expression
    | LiteralValue"""


### Expression
def p_Expression(p):
    """Expression : UnaryExpr
    | Expression binary_op Expression"""


def p_UnaryExpr(p):
    """UnaryExpr : PrimaryExpr
    | unary_op UnaryExpr"""


def p_unary_op(p):
    """unary_op : PLUS
    | MINUS
    | NOT
    | BIT_XOR
    | STAR
    | BIT_AND"""


def p_binary_op(p):
    """binary_op : OR
    | AND
    | rel_op
    | add_op
    | mul_op"""


def p_rel_op(p):
    """rel_op : EQUAL
    | NOT_EQUAL
    | LESS
    | GREATER
    | LESS_EQUAL
    | GREATER_EQUAL"""


def p_add_op(p):
    """add_op : PLUS
    | MINUS
    | BIT_OR
    | BIT_XOR"""


def p_mul_op(p):
    """mul_op : STAR
    | DIV
    | MOD
    | LEFT_SHIFT
    | RIGHT_SHIFT
    | BIT_AND"""


# 5.
def p_ShortVarDecl(p):
    """ShortVarDecl : IDENTIFIER COLON_ASSIGN Expression"""


# Function Declaration
def p_func_decl(p):
    """FunctionDecl  : FUNC FunctionName Signature  FunctionBody
    FunctionName  : IDENTIFIER
    FunctionBody  : Block
    Signature  : Parameters Result
              | Parameters
    Result  :  Type
    Parameters   : LEFT_PARENTH RIGHT_PARENTH
                | LEFT_PARENTH ParameterList RIGHT_PARENTH
    ParameterList   : ParameterDecl COMMA ParameterList
                   | ParameterDecl
    ParameterDecl   : IDENTIFIER Type"""


########
## IF ##
########
def p_IfStmt(p):
    """IfStmt : IF SimpleStmt SEMICOLON Expression Block
    | IF SimpleStmt SEMICOLON Expression Block ELSE Block
    | IF SimpleStmt SEMICOLON Expression Block ELSE IfStmt
    | IF Expression Block
    | IF Expression Block ELSE  IfStmt
    | IF Expression Block ELSE  Block
    """


def p_SwitchStmt(p):
    """SwitchStmt : SWITCH  SimpleStmt SEMICOLON Expression LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH
    | SWITCH                       Expression LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH
    | SWITCH  SimpleStmt SEMICOLON            LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH
    | SWITCH                                  LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH
    """


def p_expr_case_clause_list(p):
    """expr_case_clause_list : ExprCaseClause EOS expr_case_clause_list
    | empty
    """


## expression list external dependency
def p_ExprSwitchCase(p):
    """ExprSwitchCase : CASE ExpressionList
    | DEFAULT
    """


def p_ExprCaseClause(p):
    """ExprCaseClause : ExprSwitchCase COLON StatementList"""


def p_ForStmt(p):
    """ForStmt : FOR Block
    | FOR Expression Block
    | FOR ForClause Block
    """


def p_ForClause(p):
    """ForClause :  SimpleStmt SEMICOLON Expression SEMICOLON SimpleStmt
    | SimpleStmt SEMICOLON            SEMICOLON SimpleStmt
    """


def p_error(p):
    if p:
        print("Syntax error at token ", p.type,"  Line Number  ",p.lineno)
        # Just discard the token and tell the parser it's okay.
        parser.errok()
    else:
        print("Syntax error at EOF")


parser = yacc.yacc()
# parser.parse()

with open("../tests/parser/1.go") as f :
    program = f.read()

parser.parse(program)
# if __name__ == "__main__" :
#     parser = argparse.ArgumentParser(
#         description="A parser for the source language that outputs the Parser Automaton in a graphical form."
#     )
#     parser.add_argument("filepath", type=str, help="Path for your go program")
#     args = parser.parse_args()

#     with open(args.filepath) as f :
#         program = f.read()

#     lexer.input(program)

#     result = parser.parse(program)

#     generate_LR_automata(result)
