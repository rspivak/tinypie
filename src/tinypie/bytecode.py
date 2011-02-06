###############################################################################
#
# Copyright (c) 2011 Ruslan Spivak
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#
###############################################################################

__author__ = 'Ruslan Spivak <ruslan.spivak@gmail.com>'

# Opcode operand types: used by disassmbler
REG = 1
INT = 2
FUNC = 3
POOL = 4


class Instruction(object):

    def __init__(self, name, *operand_types):
        self.name = name
        self.operand_types = operand_types

    def __str__(self):
        return self.name

# Index serves as an opcode
INSTRUCTIONS = [
    None,
    Instruction('add', REG, REG, REG),   # A B C  R(A) = R(B) + R(C)
    Instruction('sub', REG, REG, REG),   # A B C  R(A) = R(B) - R(C)
    Instruction('mul', REG, REG, REG),   # A B C  R(A) = R(B) * R(C)
    Instruction('lt', REG, REG, REG),    # A B C  R(A) = R(B) < R(C)
    Instruction('eq', REG, REG, REG),    # A B C  R(A) = R(B) == R(C)
    Instruction('loadk', REG, POOL),     # A B    R(A) = CONST_POOL[B]
    Instruction('gload', REG, POOL),     # A B    R(A) = GLOBALS[B]
    Instruction('gstore', POOL, REG),    # A B    GLOBALS[A] = R(B)
    Instruction('ret'),
    Instruction('halt'),
    Instruction('br', INT),              # A      branch to A
    Instruction('brt', REG, INT),        # A B    R(A) is True -> branch to B
    Instruction('brf', REG, INT),        # A B    R(A) is False -> branch to B
    Instruction('move', REG, REG),       # A B    R(A) = R(B)
    Instruction('print', REG),           # A      print R(A)
    Instruction('call', FUNC, REG),      # A B    call A, R(B)
    ]

(INSTR_ADD,    # 1
 INSTR_SUB,
 INSTR_MUL,
 INSTR_LT,     # 4
 INSTR_EQ,
 INSTR_LOADK,
 INSTR_GLOAD,  # 7
 INSTR_GSTORE,
 INSTR_RET,
 INSTR_HALT,   # 10
 INSTR_BR,
 INSTR_BRT,
 INSTR_BRF,    # 13
 INSTR_MOVE,
 INSTR_PRINT,
 INSTR_CALL) = range(1, len(INSTRUCTIONS))
