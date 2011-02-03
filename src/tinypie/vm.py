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

from tinypie import bytecode
from tinypie.assembler import FunctionSymbol


class StackFrame(object):

    def __init__(self, func_symbol, return_address):
        self.func_symbol = func_symbol
        self.return_address = return_address
        self.registers = [0] * (func_symbol.args + func_symbol.locals + 1)


class VM(object):

    CALL_STACK_SIZE = 1000

    def __init__(self, assembler):
        self.main_function = assembler.main_function
        self.code = assembler.code
        self.constant_pool = assembler.constant_pool
        self.globals = [None] * assembler.global_size
        # instruction pointer
        self.ip = 0
        # call stack
        self.calls = [None] * self.CALL_STACK_SIZE
        # frame pointer
        self.fp = -1

    def execute(self):
        if self.main_function is None:
            main_function = self.main_function = FunctionSymbol(
                'main', address=0, args=0, locals=0)

        self.fp += 1
        self.calls[self.fp] = StackFrame(main_function, self.ip)
        self.ip = main_function.address
        self._cpu()

    def _cpu(self):
        """Simulate fetch-decode-execute cycle."""
        opcode = self.code[self.ip]
        while opcode != bytecode.INSTR_HALT and self.ip < len(self.code):

            # first operand of an instruction
            self.ip += 1
            # shortcut to current registers
            regs = self.calls[self.fp].registers

            if opcode == bytecode.INSTR_ADD:
                a = self._get_reg_operand()
                b = self._get_reg_operand()
                c = self._get_reg_operand()
                regs[a] = regs[b] + regs[c]

            elif opcode == bytecode.INSTR_SUB:
                a = self._get_reg_operand()
                b = self._get_reg_operand()
                c = self._get_reg_operand()
                regs[a] = regs[b] - regs[c]

            elif opcode == bytecode.INSTR_MUL:
                a = self._get_reg_operand()
                b = self._get_reg_operand()
                c = self._get_reg_operand()
                regs[a] = regs[b] * regs[c]

            elif opcode == bytecode.INSTR_PRINT:
                a = self._get_reg_operand()
                print regs[a]

            elif opcode == bytecode.INSTR_MOVE:
                a = self._get_reg_operand()
                b = self._get_reg_operand()
                regs[a] = regs[b]

            elif opcode == bytecode.INSTR_LOADK:
                a = self._get_reg_operand()
                index = self._get_int_operand()
                regs[a] = self.constant_pool[index]

            opcode = self.code[self.ip]

    def _get_reg_operand(self):
        return self._get_int_operand()

    def _get_int_operand(self):
        b1 = self.code[self.ip] & 0xff
        b2 = self.code[self.ip + 1] & 0xff
        b3 = self.code[self.ip + 2] & 0xff
        b4 = self.code[self.ip + 3] & 0xff
        word = (b1 << (8 * 3)) | (b2 << (8 * 2)) | (b3 << (8 * 2)) | b1
        self.ip += 4
        return word
