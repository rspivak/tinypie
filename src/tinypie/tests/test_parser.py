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

import unittest


class ParserTestCase(unittest.TestCase):

    def _get_parser(self, text):
        from tinypie.lexer import Lexer
        from tinypie.parser import Parser

        parser = Parser(Lexer(text))
        return parser

    def test_function_definition_no_formal_arguments(self):
        text = """
        def foo():
            print 5
        .
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_function_definition_with_arguments(self):
        text = """
        def foo(x, y):
            print 5
        .
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_function_definition_with_multiple_statements(self):
        text = """
        def foo(x, y):
            print 5
            print  7
        .
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)


    def test_function_definition_with_nl_statements(self):
        text = """
        def foo(x, y):
            print 5

            print  7

        .
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_function_definition_one_liner(self):
        text = """
        def foo(x) return 2 * x
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_function_call(self):
        text = """
        def foo(x) return 2 * x

        foo(5)
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_assign(self):
        text = """
        x = 2
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_while_multiple_statements(self):
        text = """
        while x < 10:
            x = x - 1

        .
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_while_one_liner(self):
        text = """
        while x < 10 x = x - 1
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_atom_string(self):
        text = """
        x = 'string'
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_atom_expression(self):
        text = """
        x = (7 + 3) * 5 - 2
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_atom_function_call(self):
        text = """
        def foo() return 10

        x = (7 + 3) * 5 - foo()
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_if_one_liner(self):
        text = """
        if i < 5 print i + 'less than 5'
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)

    def test_if_else_one_liner(self):
        text = """
        if i < 5 print i + 'less than 5'
        else print 'no'
        """
        parser = self._get_parser(text)
        self.assertTrue(parser.parse() is None)


