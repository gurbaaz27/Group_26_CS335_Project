###########################
## Milestone 5 : CS335A ##
######################################
## Submission Date : April 10, 2022 ##
######################################

__author__ = "Group 26, CS335A"
__filename__ = "constants.py"
__description__ = "Constants required for compiler."


SYMBOL_TABLE_DUMP_FILENAME = "symtab_{}.csv"
AST_FILENAME = "ast_{}.dot"
AST_PLOT_FILENAME = "ast_plot_{}.png"
IRCODE_FILENAME = "ircode_{}.3ac"
TOKENS_TO_IGNORE = ["{", "}", "(", ")", ";", "[", "]", ","]

MIPS_PRINTF = \
"""
__func_printf:
    addi $sp, $sp, -4
    sw $fp, ($sp)
    addi $fp, $sp, 4
    addi $sp, $sp, -4
    sw $ra, ($sp)
    addi $sp, $sp, -4
    addi $sp, $sp, 0
    li $t0, 0
    addi $t1, $fp, -16
    __printf_loop:
    lw $v0, ($t1)
    beqz $v0, __printf_loop_end
    li $t2, 1
    bne $v0, $t2, __printf_float
    add $t2, $t0, $fp
    lw $a0, ($t2)
    j __printf_end
    __printf_float:
    li $t2, 2
    bne $v0, $t2, __printf_double
    add $t2, $t0, $fp
    l.s $f12, ($t2)
    j __printf_end
    __printf_double:
    li $t2, 3
    bne $v0, $t2, __printf_string
    add $t2, $t0, $fp
    l.d $f12, ($t2)
    addi $t0, $t0, 4
    j __printf_end
    __printf_string:
    add $t2, $t0, $fp
    lw $a0, ($t2)
    __printf_end:
    syscall
    addi $t0, $t0, 4
    addi $t1, $t1, -4
    la $a0, __printf_space
    li $v0, 4
    syscall
    j __printf_loop
    __printf_loop_end:
    la $a0, __printf_newline
    li $v0, 4
    syscall
    lw $t0, -12($fp)
    sw $0, ($t0)
    li $v0, 0
    lw $ra, -8($fp)
    move $sp, $fp
    lw $fp, -4($fp)
    jr $ra
"""


MIPS_SCANF = \
"""
__func_scanf:
    addi $sp, $sp, -4
    sw $fp, ($sp)
    addi $fp, $sp, 4
    addi $sp, $sp, -4
    sw $ra, ($sp)
    addi $sp, $sp, -4
    addi $sp, $sp, 0
    li $t0, 0
    addi $t1, $fp, -16
    __scanf_loop:
    add $t2, $t0, $fp
    lw $t2, ($t2)
    move $a0, $t2
    li $a1, 1
    lw $v0, ($t1)
    beqz $v0, __scanf_loop_end
    addi $v0, $v0, 4
    syscall
    lw $t3, ($t1)
    li $t4, 1
    bne $t3, $t4, __scanf_float
    sw $v0, ($t2)
    j __scanf_end
    __scanf_float:
    li $t4, 2
    bne $t3, $t4, __scanf_double
    s.s $f0, ($t2)
    j __scanf_end
    __scanf_double:
    s.d $f0, ($t2)
    addi $t0, $t0, 4
    __scanf_end:
    addi $t0, $t0, 4
    addi $t1, $t1, -4
    la $a0, __scanf_dummy
    li $a1, 1
    li $v0, 8
    syscall
    j __scanf_loop
    __scanf_loop_end:
    la $a0, __scanf_dummy
    li $a1, 1
    li $v0, 8
    syscall
    lw $t0, -12($fp)
    sw $0, ($t0)
    li $v0, 0
    lw $ra, -8($fp)
    move $sp, $fp
    lw $fp, -4($fp)
    jr $ra
"""