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
from tinypie import asmutils
from tinypie.lexer import AssemblerLexer
from tinypie.assembler import FunctionSymbol, BytecodeAssembler


class StackFrame(object):

    def __init__(self, func_symbol, return_address):
        self.func_symbol = func_symbol
        self.return_address = return_address
        self.registers = [None] * (func_symbol.args + func_symbol.locals + 1)


class VM(object):
    """Register-Based Bytecode Interpreter.

    Example of execution trace:

    >>> from tinypie.lexer import AssemblerLexer
    >>> from tinypie.assembler import BytecodeAssembler
    >>> from tinypie.vm import VM
    >>>
    >>> text = '''
    ... .def main: args=0, locals=3
    ...     loadk r1, 5
    ...     loadk r2, 7
    ...     lt r3, r2, r1
    ...     brt r3, end
    ...     loadk r1, 13
    ... end:
    ...     call msg, r1
    ...     print r0
    ...     halt
    ... .def msg: args=1, locals=0
    ...     move r0, r1
    ...     ret
    ... '''

    >>> assembler = BytecodeAssembler(AssemblerLexer(text))
    >>> assembler.parse()
    >>> vm = VM(assembler, trace=True)
    >>> vm.execute()
    0000: LOADK   r1, #1:5       main.registers=[? | ? ? ?]    calls=[main]
    0009: LOADK   r2, #2:7       main.registers=[? | 5 ? ?]    calls=[main]
    0018: LT      r3, r2, r1     main.registers=[? | 5 7 ?]    calls=[main]
    0031: BRT     r3, 49         main.registers=[? | 5 7 0]    calls=[main]
    0040: LOADK   r1, #3:13      main.registers=[? | 5 7 0]    calls=[main]
    0049: CALL    #4:msg@64, r1  main.registers=[? | 13 7 0]   calls=[main]
    0064: MOVE    r0, r1         msg.registers=[? | 13]        calls=[main msg]
    0073: RET                    msg.registers=[13 | 13]       calls=[main msg]
    0058: PRINT   r0             main.registers=[13 | 13 7 0]  calls=[main]
    13

    """

    CALL_STACK_SIZE = 1000

    def __init__(self, assembler, trace=False):
        self.main_function = assembler.main_function
        self.code = assembler.code
        self.code_size = assembler.code_size
        self.constant_pool = assembler.constant_pool
        self.globals = [None] * assembler.global_size
        # instruction pointer
        self.ip = 0
        # call stack
        self.calls = [None] * self.CALL_STACK_SIZE
        # frame pointer
        self.fp = -1
        self.trace = trace
        # initialize disassmbler
        self.disasm = asmutils.DisAssembler(
            self.code, self.code_size, self.constant_pool)

    def execute(self):
        if self.main_function is None:
            self.main_function = FunctionSymbol(
                'main', address=0, args=0, locals=0)

        self.fp += 1
        self.calls[self.fp] = StackFrame(self.main_function, self.ip)
        self.ip = self.main_function.address
        self._cpu()

    def coredump(self):
        md = asmutils.MemoryDump(
            self.code, self.code_size, self.globals, self.constant_pool)
        md.coredump()

    def disassemble(self):
        self.disasm.disassemble()

    def _cpu(self):
        """Simulate fetch-decode-execute cycle."""
        opcode = self.code[self.ip]
        while opcode != bytecode.INSTR_HALT and self.ip < self.code_size:
            if self.trace:
                self._trace()
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
        word = asmutils.get_int(self.code, self.ip)
        self.ip += 4
        return word

    def _trace(self):
        _, instr_text = self.disasm.disassemble_instruction(self.code, self.ip)
        registers = self.calls[self.fp].registers
        func_symbol = self.calls[self.fp].func_symbol

        result = '%s.registers=[' % func_symbol.name
        for index, reg_value in enumerate(registers):

            if index in (1, func_symbol.args + 1):
                result += ' |'

            if index != 0:
                result += ' '

            if reg_value is None:
                result += '?'
            else:
                if isinstance(reg_value, str):
                    reg_value = "'%s'" % reg_value
                result += str(reg_value)

        result += ']'
        regs_out = '{registers:20}'.format(registers=result)

        calls_out = 'calls=['
        index = 0
        while index <= self.fp:
            calls_out += self.calls[index].func_symbol.name
            if index != self.fp:
                calls_out += ' '
            index += 1
        calls_out += ']'

        print '{instruction:30} {registers:35} {calls}'.format(
            instruction=instr_text, registers=regs_out, calls=calls_out)


def main():
    usage = textwrap.dedent("""\
    %prog [input file]

    If no input file is provided STDIN is used by default.
    """)
    parser = optparse.OptionParser(usage=usage)
    parser.add_option('-i', '--input',
                      dest='file',
                      help='Input file. Defaults to standard input.')
    parser.add_option('-c', '--coredump', action='store_true', dest='coredump',
                      help='Print coredump to standard output.')
    parser.add_option('-d', '--disasm', action='store_true', dest='disasm',
                      help='Print disassembled code to standard output.')
    parser.add_option('-t', '--trace', action='store_true', dest='trace',
                      help='Print execution trace.')
    options, args = parser.parse_args()

    if options.file is not None:
        text = open(options.file).read()
    else:
        text = sys.stdin.read()

    assembler = BytecodeAssembler(AssemblerLexer(text))
    assembler.parse()
    vm = VM(assembler, trace=options.trace)
    vm.execute()

    if options.coredump:
        vm.coredump()

    if options.disasm:
        vm.disassemble()
