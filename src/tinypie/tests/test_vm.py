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
import unittest
import StringIO

from contextlib import contextmanager


@contextmanager
def redirected_output():
    old = sys.stdout
    out = StringIO.StringIO()
    sys.stdout = out
    try:
        yield out
    finally:
        sys.stdout = old


class VMTestCase(unittest.TestCase):

    def _get_vm(self, text):
        from tinypie.lexer import AssemblerLexer
        from tinypie.assembler import BytecodeAssembler
        from tinypie.vm import VM
        assembler = BytecodeAssembler(AssemblerLexer(text))
        assembler.parse()
        vm = VM(assembler)
        return vm

    def test_vm(self):
        text = """
            loadk r1, 5
            print r1
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 5)
