"""
Author: Alex Bazo
"""

# list of all possible instructions
OPCODES = ['MOVE', 'CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'DEFVAR', 'CALL', 'RETURN',
           'PUSHS', 'POPS',
           'ADD', 'SUB', 'MUL', 'IDIV',
           'LT', 'GT', 'EQ',
           'AND', 'OR', 'NOT',
           'INT2CHAR', 'STRI2INT',
           'READ', 'WRITE',
           'CONCAT', 'STRLEN', 'GETCHAR', 'SETCHAR',
           'TYPE',
           'LABEL', 'JUMP', 'JUMPIFEQ', 'JUMPIFNEQ', 'EXIT',
           'DPRINT', 'BREAK',
           'CLEARS', 'ADDS', 'SUBS', 'MULS', 'IDIVS', 'LTS', 'GTS', 'EQS', 'ANDS', 'ORS', 'NOTS', 'INT2CHARS', 'STRI2INTS',
           'JUMPIFEQS', 'JUMPIFNEQS']

# same instructions, but sorted to lists by number of arguments they get
ARGC0 = ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK',
         'CLEARS', 'ADDS', 'SUBS', 'MULS', 'IDIVS', 'LTS', 'GTS', 'EQS', 'ANDS', 'ORS', 'NOTS', 'INT2CHARS', 'STRI2INTS']
ARGC1 = ['DEFVAR', 'CALL', 'PUSHS', 'POPS', 'WRITE', 'LABEL', 'JUMP', 'EXIT', 'DRPINT', 'JUMPIFEQS', 'JUMPIFNEQS']
ARGC2 = ['MOVE', 'INT2CHAR', 'READ', 'STRLEN', 'TYPE', 'NOT']
ARGC3 = ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'STRI2INT', 'CONCAT', 'GETCHAR', 'SETCHAR',
         'JUMPIFEQ', 'JUMPIFNEQ']


#  file sources
source = ""  # XML source file
input = ""  # program input file
