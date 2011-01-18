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


class InterpreterTestCase(unittest.TestCase):

    def _get_interpreter(self):
        from tinypie.interpreter import Interpreter
        interp = Interpreter()
        return interp

    def test_print_integer(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            print 5
            """)
        self.assertEquals(output.getvalue().strip(), '5')

    def test_print_string(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            print 'string'
            """)
        self.assertEquals(output.getvalue().strip(), "'string'")

    def test_assign(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            x = 5
            print x
            """)
        self.assertEquals(output.getvalue().strip(), '5')

    def test_function_call(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            def foo(x):
                print x
            .

            foo(15)
            """)
        self.assertEquals(output.getvalue().strip(), '15')


