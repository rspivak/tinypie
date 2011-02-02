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


class MemoryDump(object):
    """Dumps code memory, data memory(globals), and constant pool."""

    def __init__(self, code_memory, data_memory, constant_pool):
        self.code_memory = code_memory
        self.data_memory = data_memory
        self.constant_pool = constant_pool

    def coredump(self):
        """Dump memory.

        >>> from tinypie.lexer import AssemblerLexer
        >>> from tinypie.assembler import BytecodeAssembler
        >>> from tinypie.asmutils import MemoryDump
        >>>
        >>> text = '''
        ...     br label
        ...     halt
        ... label:
        ...     call foo, r3
        ... .def foo: args=2, locals=1
        ...     halt
        ... '''

        >>> parser = BytecodeAssembler(AssemblerLexer(text))
        >>> parser.parse()
        >>> md = MemoryDump(parser.code, [], parser.constant_pool)
        >>> md.coredump()
        Constant pool:
        0000: <FunctionSymbol: name='foo', address=15, args=2, locals=1>
        <BLANKLINE>
        Code memory:
        0000:  11   0   0   0   6  10  16   0
        0008:   0   0   0   0   0   0   3  10
        0016:   0   0

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
        for index, byte_value in enumerate(self.code_memory):
            if index % 8 == 0 and index != 0:
                result += '\n'
            if index % 8 == 0:
                result += '%04d:' % index

            result += ' %3d' % byte_value

        print result
