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


class Instruction(object):

    def __init__(self, name, *operands):
        self.name = name
        #self.types = list(operands)

# Index serves as an opcode
INSTRUCTIONS = [
    None,
    Instruction('add'),       # A B C  R(A) = R(B) + R(C)
    Instruction('sub'),       # A B C  R(A) = R(B) - R(C)
    Instruction('mul'),       # A B C  R(A) = R(B) * R(C)
    Instruction('lt'),        # A B C  R(A) = R(B) < R(C)
    Instruction('eq'),        # A B C  R(A) = R(B) == R(C)
    Instruction('loadk'),     # A B    R(A) = CONST_POOL[B]
    Instruction('gload'),     # A B    R(A) = GLOBALS[B]
    Instruction('gstore'),    # A B    GLOBALS[A] = R(B)
    Instruction('ret'),
    Instruction('halt'),
    Instruction('br'),        # A      branch to A
    Instruction('brt'),       # A B    R(A) is True -> branch to B
    Instruction('brf'),       # A B    R(A) is False -> branch to B
    Instruction('move'),      # A B    R(A) = R(B)
    Instruction('print'),     # A      print R(A)
    Instruction('call'),      # A B    call A, R(B)
    ]

(INSTR_ADD,
 INSTR_SUB,
 INSTR_MUL,
 INSTR_LT,
 INSTR_EQ,
 INSTR_LOADK,
 INSTR_GLOAD,
 INSTR_GSTORE,
 INSTR_RET,
 INSTR_HALT,
 INSTR_BR,
 INSTR_BRT,
 INSTR_BRF,
 INSTR_MOVE,
 INSTR_PRINT,
 INSTR_CALL) = range(1, len(INSTRUCTIONS))
