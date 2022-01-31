# Milestone-II

## Tokens for Lexer

### Reserved I: Keywords

```
break       default         func         ~interface~    ~select~
case        ~defer~         ~go~         ~map~          struct
~chan~      else            ~goto~       package        switch
const       ~fallthrough~   if           range          type
continue    for             import       return         var
```

> __*Capitalise them to form tokens*__

### Reserved II: Special Meaning Words

```
int.....8 16 32 64
uint...8 16 32 64
float...32 64
string...
boolean...
```

> __*Capitalise them to form tokens*__

### Operators and Punctuations

```
+     &     +=    &=     &&    ==    !=   (    )
-     |     -=    |=     ||    <     <=    [    ]
*     ^     *=    ^=     <-    >     >=    {    }
/    <<    /=    <<=    ++    =     :=    ,    ;
%    >>    %=    >>=    --    !     ...   .    :
```

> __*Make meaningful descriptive token names*__


### Miscellaneous

- IDENTIFIER: `main`, `factorial`, `x`

- COMMENT: `//` or `/* ... */`

- NEWLINE: `\n`

- INTEGER_LITERAL: `3`, `0x4`, `0o25`
    - decimal_lit 
    - binary_lit    
    - octal_lit 
    - hex_lit

- FLOAT_LITERAL: `1e+05`, `.35`

- BOOLEN_LITERAL: `true`, `false`

- STRING_LITERAL: `"hello"`, `"bye"` 

- IGNORE: `\t`, `' '`(whitespace)