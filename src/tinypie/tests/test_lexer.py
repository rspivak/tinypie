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

from tinypie import tokens


class LexerTestCase(unittest.TestCase):

    def _get_token(self, text):
        from tinypie.lexer import Lexer
        lexer = Lexer(text)

        return lexer.token()

    def test_def(self):
        token = self._get_token('def')
        self.assertEquals(token.type, tokens.DEF)

    def test_print(self):
        token = self._get_token('print')
        self.assertEquals(token.type, tokens.PRINT)

    def test_return(self):
        token = self._get_token('return')
        self.assertEquals(token.type, tokens.RETURN)

    def test_if(self):
        token = self._get_token('if')
        self.assertEquals(token.type, tokens.IF)

    def test_else(self):
        token = self._get_token('else')
        self.assertEquals(token.type, tokens.ELSE)

    def test_while(self):
        token = self._get_token('while')
        self.assertEquals(token.type, tokens.WHILE)

    def test_id(self):
        token = self._get_token('obj_id')
        self.assertEquals(token.type, tokens.ID)

    def test_int(self):
        token = self._get_token('777')
        self.assertEquals(token.type, tokens.INT)

    def test_string(self):
        token = self._get_token("'str'")
        self.assertEquals(token.type, tokens.STRING)

    def test_lparen(self):
        token = self._get_token('(')
        self.assertEquals(token.type, tokens.LPAREN)

    def test_rparen(self):
        token = self._get_token(')')
        self.assertEquals(token.type, tokens.RPAREN)

    def test_dot(self):
        token = self._get_token(' . ')
        self.assertEquals(token.type, tokens.DOT)

    def test_comma(self):
        token = self._get_token(' , ')
        self.assertEquals(token.type, tokens.COMMA)

    def test_eq(self):
        token = self._get_token('==')
        self.assertEquals(token.type, tokens.EQ)

    def test_lt(self):
        token = self._get_token('<')
        self.assertEquals(token.type, tokens.LT)

    def test_add(self):
        token = self._get_token(' +')
        self.assertEquals(token.type, tokens.ADD)

    def test_sub(self):
        token = self._get_token('-')
        self.assertEquals(token.type, tokens.SUB)

    def test_mul(self):
        token = self._get_token(' * ')
        self.assertEquals(token.type, tokens.MUL)

    def test_assign(self):
        token = self._get_token('=')
        self.assertEquals(token.type, tokens.ASSIGN)

    def test_nl_return(self):
        token = self._get_token('\r\n')
        self.assertEquals(token.type, tokens.NL)

    def test_nl(self):
        token = self._get_token(' \n')
        self.assertEquals(token.type, tokens.NL)
