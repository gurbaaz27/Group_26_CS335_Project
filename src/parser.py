precedence = (
    ('left', 'COMMA'),
    ('right', 'ASSIGN', 'PLUS_ASSIGN', 'MINUS_ASSIGN', 'STAR_ASSIGN',
     'DIV_ASSIGN', 'MOD_ASSIGN', 'AND_ASSIGN', 'OR_ASSIGN', 'XOR_ASSIGN',
     'COLON_ASSIGN', 'RIGHT_SHIFT_EQUAL', 'LEFT_SHIFT_EQUAL'),
    ('left', 'OR'),
    ('left', 'AND'),
    ('left', 'BIT_OR'),
    ('left', 'BIT_XOR'),
    ('left', 'BIT_AND'),
    ('left', 'EQUAL', 'NOT_EQUAL'),
    ('left', 'LESS_EQUAL', 'GREATER_EQUAL', 'LESS', 'GREATER'),
    ('left', 'RIGHT_SHIFT', 'LEFT_SHIFT'),
    ('left', 'PLUS', 'MINUS'),
    ('left', 'STAR', 'DIV', 'MOD'),
    ('right', 'NOT', 'UPLUS', 'UMINUS', 'INCREMENT', 'DECREMENT',
     'DEREF_AND', 'POINTER_STAR'),
    # Take care of functions, array/slice element and structs
)

def p_start(p):
    """start: Sourcefile"""

def p_empty(p):
    """empty:"""

#change it
def p_expression(p):
    """expression: LEFT_PARENTH expression RIGHT_PARENTH
                 | expression OR expression
                 | expression AND expression
                 | expression BIT_OR expression
                 | expression BIT_XOR expression
                 | expression BIT_AND expression
                 | expression EQUAL expression
                 | expression NOT_EQUAL expression
                 | expression LESS_EQUAL expression
                 | expression GREATER_EQUAL expression
                 | expression LESS expression
                 | expression GREATER expression
                 | expression RIGHT_SHIFT expression
                 | expression LEFT_SHIFT expression
                 | expression PLUS expression
                 | expression MINUS expression
                 | expression STAR expression
                 | expression DIV expression
                 | expression MOD expression
                 | NOT expression
                 | MINUS expression %prec UMINUS
                 | PLUS expression %prec UPLUS
                 | INCREMENT variable
                 | variable INCREMENT
                 | DECREMENT variable
                 | variable DECREMENT
                 | STAR variable %prec POINTER_STAR
                 | BIT_AND variable %prec DEREF_AND
                 | variable
                 | number
    """
#handle increment decrement, reference, pointer
#handle function, array, slice, struct
def p_struct_element(p):
    """struct_element: array_element DOT IDENTIFIER
                     | struct_element DOT IDENTIFIER
    """

def p_variable(p):
    """variable: IDENTIFIER
               | array_element
               | struct_element
    """

def p_basic_dec(p):
    """basic_dec: VAR IDENTIFIER types 
    """

def p_constants(p):
    """constants: INTCONST
                | FLOATCONST
                | BOOLCONST
                | STRINGCONST
    """

def p_number(p):
    """number: INTCONST
             | FLOATCONST
             | BOOLCONST
    """

##### Eos #####

def p_Eos(p):
    """ Eos: NEWLINE
           | SEMICOLON
    """
##### Type #####

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

def TypeLit(p):
    """TypeLit: StructType
              | ArrayType
              | Slicetype
              | PointerType
    """

def p_PointerType(p):
    """PointerType: STAR Type
    """

def p_Type(p):
    """Type: TypeName
           | TypeLit
           | LEFT_PARENTH Type RIGHT_PARENTH
    """
##### Array #####

def p_ArrayType(p):
    """ArrayType: LEFT_SQUARE ArrayLength RIGHT_SQUARE ElementType
    """

def p_ArrayLength(p):
    """ArrayLength: Expression
    """

def p_ElementType(p):
    """ElementType: Type
    """
##### Slice #####

def p_SliceType(p):
    """SliceType: LEFT_SQUARE RIGHT_SQUARE ElementType
    """
##### Struct #####

def p_StructType(p):
    """StructType: STRUCT LEFT_BRACE Fields RIGHT_BRACE
    """

def p_Fields(p):
    """Fields: FieldDecl Eos
             | FieldDecl Eos Fields
    """

def p_FieldDecl(p):
    """FieldDecl: IDENTIFIER Type
    """
    
# Function Declaration
def p_func_decl(p):
  '''FunctionDecl : FUNC FunctionName Signature  FunctionBody  
     FunctionName : identifier 
     FunctionBody : Block 
     Signature    : Parameters Result
                  | Parameters
     Result       :  Type 
    Parameters    : LEFT_PARENTH RIGHT_PARENTH
                  | LEFT_PARENTH ParameterList RIGHT_PARENTH
    ParameterList  : ParameterDecl COMMA ParameterList
                   | ParameterDecl  
    ParameterDecl  : identifier Type '''


################################################################
#my task
###############################################
## ehde ch doubt eh aa ki group karke ghta skde aa ke ni - specifically else ton baad aala part
def p_IfStmt (p):
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
    """  SwitchStmt: SWITCH  SimpleStmt SEMICOLON Expression LEFT_PARENTH  expr_case_clause_list RIGHT_PARENTH 
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
    """ExprCaseClause: ExprSwitchCase COLON StatementList
    """

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

