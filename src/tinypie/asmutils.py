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


def get_int(code, address):
    b1 = code[address] & 0xff
    b2 = code[address + 1] & 0xff
    b3 = code[address + 2] & 0xff
    b4 = code[address + 3] & 0xff
    word = (b1 << (8 * 3)) | (b2 << (8 * 2)) | (b3 << 8) | b4
    return word


class MemoryDump(object):
    """Dumps code memory, data memory(globals), and constant pool."""

    def __init__(self, code_memory, code_size, data_memory, constant_pool):
        self.code_memory = code_memory
        self.code_size = code_size
        self.data_memory = data_memory
        self.constant_pool = constant_pool

    def coredump(self):
        """Dump memory.

        >>> from tinypie.lexer import AssemblerLexer
        >>> from tinypie.assembler import BytecodeAssembler
        >>> from tinypie.vm import VM
        >>> from tinypie.asmutils import MemoryDump
        >>>
        >>> text = '''
        ... .globals 1
        ... .def main: args=0, locals=1
        ...     br label
        ...     halt
        ... label:
        ...     loadk r1, 'hi'
        ...     gstore 0, r1
        ...     call foo, r1
        ...     halt
        ... .def foo: args=1, locals=0
        ...     print r1
        ... '''

        >>> assembler = BytecodeAssembler(AssemblerLexer(text))
        >>> assembler.parse()
        >>> vm = VM(assembler)
        >>> vm.execute()
        hi
        >>>
        >>> md = MemoryDump(
        ...     vm.code, vm.code_size, vm.globals, vm.constant_pool)
        >>> md.coredump()
        Constant pool:
        0000: <FunctionSymbol: name='main', address=0, args=0, locals=1>
        0001: 'hi'
        0002: 0
        0003: <FunctionSymbol: name='foo', address=34, args=1, locals=0>
        <BLANKLINE>
        Data memory:
        0000: hi <str>
        <BLANKLINE>
        Code memory:
        0000:  11   0   0   0   6  10   6   0
        0008:   0   0   1   0   0   0   1   8
        0016:   0   0   0   2   0   0   0   1
        0024:  16   0   0   0   3   0   0   0
        0032:   1  10  15   0   0   0   1

        """
        if self.constant_pool:
            self._dump_constant_pool()

        if self.data_memory:
            self._dump_data_memory()

        self._dump_code_memory()

    def _dump_constant_pool(self):
        print 'Constant pool:'
        for index, item in enumerate(self.constant_pool):
            if isinstance(item, str):
                print "%04d: '%s'" % (index, item)
            else:
                print '%04d: %s' % (index, item)
        print

    def _dump_data_memory(self):
        print 'Data memory:'
        for index, item in enumerate(self.data_memory):
            print '%04d: %s <%s>' % (index, item, item.__class__.__name__)
        print

    def _dump_code_memory(self):
        print 'Code memory:'
        result = ''
        for index in range(self.code_size):
            byte_value = self.code_memory[index]
            if index % 8 == 0 and index != 0:
                result += '\n'
            if index % 8 == 0:
                result += '%04d:' % index

            result += ' %3d' % byte_value

        print '%s\n' % result


class DisAssembler(object):
    """Bytecode disassembler.

    When printing values from constant pool the following format is used:
    #pool_index:pool_value

    Function format for CALL instruction:
    #pool_index:func_name@func_address

    >>> from tinypie.lexer import AssemblerLexer
    >>> from tinypie.assembler import BytecodeAssembler
    >>> from tinypie.vm import VM
    >>> from tinypie.asmutils import DisAssembler
    >>>
    >>> text = '''
    ... .globals 1
    ... .def main: args=0, locals=1
    ...     br label
    ...     halt
    ... label:
    ...     loadk r1, 'hi'
    ...     gstore 0, r1
    ...     call foo, r1
    ...     halt
    ... .def foo: args=1, locals=0
    ...     print r1
    ... '''

    >>> assembler = BytecodeAssembler(AssemblerLexer(text))
    >>> assembler.parse()
    >>> dis = DisAssembler(
    ...     assembler.code, assembler.code_size, assembler.constant_pool)
    >>> dis.disassemble()
    Disassembly:
    0000: BR      6
    0005: HALT
    0006: LOADK   r1, #1:'hi'
    0015: GSTORE  #2:0, r1
    0024: CALL    #3:foo@34, r1
    0033: HALT
    0034: PRINT   r1

    """

    def __init__(self, code, code_size, constant_pool):
        self.code = code
        self.code_size = code_size
        self.constant_pool = constant_pool

    def disassemble(self):
        print 'Disassembly:'
        index = 0
        while index < self.code_size:
            index, output = self.disassemble_instruction(self.code, index)
            print output

    def disassemble_instruction(self, code, ip):
        opcode = code[ip]
        instruction = bytecode.INSTRUCTIONS[opcode]
        index = ip + 1
        result = []

        for operand_type in instruction.operand_types:
            if operand_type == bytecode.INT:
                result.append(str(get_int(self.code, index)))
                index += 4

            elif operand_type == bytecode.REG:
                result.append('r%s' % get_int(self.code, index))
                index += 4

            elif operand_type == bytecode.FUNC:
                pool_index = get_int(self.code, index)
                func_symbol = self.constant_pool[pool_index]
                value = '#{pool_index}:{func_name}@{func_address}'.format(
                    pool_index=pool_index, func_name=func_symbol.name,
                    func_address=func_symbol.address)
                result.append(value)
                index += 4

            elif operand_type == bytecode.POOL:
                pool_index = get_int(self.code, index)
                value = self.constant_pool[pool_index]
                if isinstance(value, str):
                    value = "'%s'" % value
                value = '#{pool_index}:{value}'.format(
                    pool_index=pool_index, value=value)
                result.append(str(value))
                index += 4

        output = '{address:04}: {instr_name:8}{operands}'.format(
            address=ip, instr_name=instruction.name.upper(),
            operands=', '.join(result))

        return index, output
