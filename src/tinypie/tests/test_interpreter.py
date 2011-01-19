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
        self.assertEquals(output.getvalue().strip(), 'string')

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

    def test_function_call_with_return(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            def foo(x):
                return x
            .

            result = foo(3)
            print result
            """)
        self.assertEquals(output.getvalue().strip(), '3')

    def test_function_call_multiple_func_statements(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            def foo(x, y):
                z = x + y
                return z
            .

            print foo(3, 7)
            """)
        self.assertEquals(output.getvalue().strip(), '10')

    def test_function_call_one_liner(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            def foo(x) return x * x

            print foo(3) + 2 * (7 - 2)
            """)
        self.assertEquals(output.getvalue().strip(), '19')

    def test_add_expr(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            x = 7
            print x + 3
            """)
        self.assertEquals(output.getvalue().strip(), '10')

    def test_sub_expr(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            x = 7
            print x - 3
            """)
        self.assertEquals(output.getvalue().strip(), '4')

    def test_mul_expr(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            x = 7
            print x * 3
            """)
        self.assertEquals(output.getvalue().strip(), '21')

    def test_if_statement_oneliner(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            x = 1
            if x < 10 print x
            """)
        self.assertEquals(output.getvalue().strip(), '1')

    def test_if_else_statement_oneliner(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            x = 10
            if x < 10 print x
            else print 'No'
            """)
        self.assertEquals(output.getvalue().strip(), 'No')

    def test_compare_equal(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            if 5 + 5 == 10 print 'Yes'
            else print 'No'
            """)
        self.assertEquals(output.getvalue().strip(), 'Yes')

    def test_while_op(self):
        interp = self._get_interpreter()
        with redirected_output() as output:
            interp.interpret("""
            x = 0
            y = 10
            def double(x) return 2 * x

            while x < 3:
                y = y + double(x)
                x = x + 1
            .
            print y
            """)
        self.assertEquals(output.getvalue().strip(), '16')
