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

    def test_loadk(self):
        text = """
        .def main: args=0, locals=1
            loadk r1, 5
            print r1
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 5)

    def test_add(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 7
            loadk r2, 5
            add r3, r1, r2
            print r3
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 12)

    def test_sub(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 7
            loadk r2, 5
            sub r3, r1, r2
            print r3
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 2)

    def test_mul(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 7
            loadk r2, 5
            mul r3, r1, r2
            print r3
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 35)

    def test_move(self):
        text = """
        .def main: args=0, locals=2
            loadk r1, 7
            move r2, r1
            print r2
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 7)

    def test_lt_false(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 7
            loadk r2, 5
            lt r3, r1, r2
            print r3
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 0)

    def test_lt_true(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 7
            loadk r2, 5
            lt r3, r2, r1
            print r3
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 1)

    def test_eq_false(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 7
            loadk r2, 5
            eq r3, r1, r2
            print r3
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 0)

    def test_eq_true(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 5
            loadk r2, 5
            eq r3, r1, r2
            print r3
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 1)

    def test_br(self):
        text = """
        .def main: args=0, locals=1
            loadk r1, 5
            br end
            loadk r1, 7
        end:
            print r1
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 5)

    def test_brt_true(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 5
            loadk r2, 7
            lt r3, r1, r2
            brt r3, end
            loadk r1, 13
        end:
            print r1
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 5)

    def test_brt_false(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 5
            loadk r2, 7
            lt r3, r2, r1
            brt r3, end
            loadk r1, 13
        end:
            print r1
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 13)

    def test_brf_true(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 5
            loadk r2, 7
            lt r3, r2, r1
            brf r3, end
            loadk r1, 13
        end:
            print r1
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 5)

    def test_brf_false(self):
        text = """
        .def main: args=0, locals=3
            loadk r1, 5
            loadk r2, 7
            lt r3, r1, r2
            brf r3, end
            loadk r1, 13
        end:
            print r1
        """
        vm = self._get_vm(text)
        with redirected_output() as output:
            vm.execute()
        self.assertEquals(int(output.getvalue().strip()), 13)
