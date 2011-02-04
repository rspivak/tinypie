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

import sys
import optparse
import textwrap

from tinypie import bytecode
from tinypie.asmutils import MemoryDump
from tinypie.lexer import AssemblerLexer
from tinypie.assembler import FunctionSymbol, BytecodeAssembler


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
        self.globals = [0] * assembler.global_size
        # instruction pointer
        self.ip = 0
        # call stack
        self.calls = [None] * self.CALL_STACK_SIZE
        # frame pointer
        self.fp = -1

    def execute(self):
        if self.main_function is None:
            self.main_function = FunctionSymbol(
                'main', address=0, args=0, locals=0)

        self.fp += 1
        self.calls[self.fp] = StackFrame(self.main_function, self.ip)
        self.ip = self.main_function.address
        self._cpu()

    def coredump(self):
        md = MemoryDump(self.code, self.globals, self.constant_pool)
        md.coredump()

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

            elif opcode == bytecode.INSTR_LT:
                a = self._get_reg_operand()
                b = self._get_reg_operand()
                c = self._get_reg_operand()
                regs[a] = int(regs[b] < regs[c])

            elif opcode == bytecode.INSTR_EQ:
                a = self._get_reg_operand()
                b = self._get_reg_operand()
                c = self._get_reg_operand()
                regs[a] = int(regs[b] == regs[c])

            elif opcode == bytecode.INSTR_BR:
                address = self._get_int_operand()
                self.ip = address

            elif opcode == bytecode.INSTR_BRT:
                a = self._get_reg_operand()
                address = self._get_int_operand()
                if bool(regs[a]):
                    self.ip = address

            elif opcode == bytecode.INSTR_BRF:
                a = self._get_reg_operand()
                address = self._get_int_operand()
                if not bool(regs[a]):
                    self.ip = address

            elif opcode == bytecode.INSTR_GSTORE:
                index = self._get_int_operand()
                a = self.constant_pool[index]
                b = self._get_reg_operand()
                self.globals[a] = regs[b]

            elif opcode == bytecode.INSTR_GLOAD:
                a = self._get_reg_operand()
                index = self._get_int_operand()
                b = self.constant_pool[index]
                regs[a] = self.globals[b]

            elif opcode == bytecode.INSTR_CALL:
                self._call()

            elif opcode == bytecode.INSTR_RET:
                stack_frame = self.calls[self.fp]
                self.fp -= 1
                self.calls[self.fp].registers[0] = stack_frame.registers[0]
                self.ip = stack_frame.return_address

            opcode = self.code[self.ip]

    def _call(self):
        calling_frame = self.calls[self.fp]
        index = self._get_int_operand()
        base_reg = self._get_int_operand()
        func_symbol = self.constant_pool[index]
        stack_frame = StackFrame(func_symbol, self.ip)

        for a in range(func_symbol.args):
            stack_frame.registers[a + 1] = \
                                    calling_frame.registers[base_reg + a]

        self.fp += 1
        self.calls[self.fp] = stack_frame
        self.ip = func_symbol.address

    def _get_reg_operand(self):
        return self._get_int_operand()

    def _get_int_operand(self):
        b1 = self.code[self.ip] & 0xff
        b2 = self.code[self.ip + 1] & 0xff
        b3 = self.code[self.ip + 2] & 0xff
        b4 = self.code[self.ip + 3] & 0xff
        word = (b1 << (8 * 3)) | (b2 << (8 * 2)) | (b3 << 8) | b4
        self.ip += 4
        return word


def main():
    usage = textwrap.dedent("""\
    %prog [input file]

    If no input file is provided STDIN is used by default.
    """)
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--input',
                      dest='file',
                      help='Input file. Defaults to standard input.')
    options, args = parser.parse_args()

    if options.file is not None:
        text = open(options.file).read()
    else:
        text = sys.stdin.read()

    assembler = BytecodeAssembler(AssemblerLexer(text))
    assembler.parse()
    vm = VM(assembler)
    vm.execute()
