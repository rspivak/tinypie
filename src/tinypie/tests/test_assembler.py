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

import doctest
import unittest


class BytecodeAssemblerTestCase(unittest.TestCase):

    def _get_parser(self, text):
        from tinypie.lexer import AssemblerLexer
        from tinypie.assembler import BytecodeAssembler

        parser = BytecodeAssembler(AssemblerLexer(text))
        return parser

    def test_globals(self):
        text = """
        .globals 5
        """
        parser = self._get_parser(text)
        parser.parse()
        self.assertEquals(parser.global_size, 5)

    def test_label_definition(self):
        text = """
        end:
            print r3
            brt r1, end
        """
        parser = self._get_parser(text)
        self.assertEquals(len(parser.labels), 0)
        parser.parse()
        self.assertEquals(len(parser.labels), 1)
        self.assertTrue('end' in parser.labels)
        self.assertEquals(parser.code[13], 0)

    def test_label_backpatching(self):
        text = """
            br end1
            br end2
            halt
        end1:
            halt
        end2:
            halt
        """
        parser = self._get_parser(text)
        self.assertEquals(len(parser.labels), 0)
        parser.parse()
        self.assertEquals(len(parser.labels), 2)
        self.assertTrue('end1' in parser.labels)
        self.assertTrue('end2' in parser.labels)
        # address of end1 is 11
        self.assertEquals(parser.code[4], 11)
        # address of end2 is 12
        self.assertEquals(parser.code[9], 12)

    def test_function_definition(self):
        text = """
        .def main: args=2, locals=3
        """
        parser = self._get_parser(text)
        self.assertEquals(len(parser.constant_pool), 0)
        self.assertTrue(parser.main_function is None)
        parser.parse()
        self.assertEquals(len(parser.constant_pool), 1)
        self.assertTrue(parser.main_function is not None)

        func_sym = parser.constant_pool[0]
        self.assertEquals(func_sym.name, 'main')
        self.assertEquals(func_sym.args, 2)
        self.assertEquals(func_sym.locals, 3)
        self.assertEquals(func_sym.address, 0)

    def test_halt_instruction(self):
        from tinypie import bytecode
        text = """
        halt
        """
        parser = self._get_parser(text)
        parser.parse()
        # check that opcode is a HALT instruction
        self.assertEquals(parser.code[0], bytecode.INSTR_HALT)

    def test_absolute_branch_instruction(self):
        from tinypie import bytecode
        text = """
            br label
        label:
        """
        parser = self._get_parser(text)
        parser.parse()
        # check that the opcode is a BR instruction
        self.assertEquals(parser.code[0], bytecode.INSTR_BR)
        # check that the lowest byte of the instruction has value 5
        self.assertEquals(parser.code[4], 5)

    def test_add_instruction(self):
        from tinypie import bytecode
        text = """
        add r3, r1, r2
        """
        parser = self._get_parser(text)
        parser.parse()
        # check that the opcode is an ADD instruction
        self.assertEquals(parser.code[0], bytecode.INSTR_ADD)
        # check then register numbers
        self.assertEquals(parser.code[4], 3)
        self.assertEquals(parser.code[8], 1)
        self.assertEquals(parser.code[12], 2)

    def test_loadk_int_instruction(self):
        from tinypie import bytecode
        text = """
        loadk r2, 7
        """
        parser = self._get_parser(text)
        parser.parse()
        # check that the opcode is a LOADK instruction
        self.assertEquals(parser.code[0], bytecode.INSTR_LOADK)
        # check the register number
        self.assertEquals(parser.code[4], 2)
        # check the index of constant pool for 7
        self.assertEquals(parser.code[8], 0)

    def test_loadk_string_instruction(self):
        from tinypie import bytecode
        text = """
        loadk r3, 'hello'
        loadk r2, 'hi'
        """
        parser = self._get_parser(text)
        parser.parse()
        # check that the opcode is a LOADK instruction
        self.assertEquals(parser.code[9], bytecode.INSTR_LOADK)
        # check the register number
        self.assertEquals(parser.code[13], 2)
        # check the index of constant pool for 'hi'
        self.assertEquals(parser.code[17], 1)

    def test_call_instruction(self):
        from tinypie import bytecode
        text = """
            call bar, r3
            call foo, r2
        .def foo: args=2, locals=3
        """
        parser = self._get_parser(text)
        parser.parse()
        # check that the opcode is a CALL instruction
        self.assertEquals(parser.code[0], bytecode.INSTR_CALL)
        # check that the opcode is a CALL instruction
        self.assertEquals(parser.code[9], bytecode.INSTR_CALL)
        # check the index of constant pool for 'bar'
        self.assertEquals(parser.code[4], 0)
        # check the index of constant pool for 'foo'
        self.assertEquals(parser.code[13], 1)
        # check the register number for 'bar'
        self.assertEquals(parser.code[8], 3)
        # check the register number for 'foo'
        self.assertEquals(parser.code[17], 2)
        # check the address in constant pool
        func_symbol = parser.constant_pool[1]
        self.assertEquals(func_symbol.name, 'foo')
        self.assertEquals(func_symbol.address, 18)


def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(BytecodeAssemblerTestCase),
        doctest.DocFileSuite(
            '../asmutils.py',
            optionflags=doctest.NORMALIZE_WHITESPACE|doctest.ELLIPSIS
            ),
        ))
