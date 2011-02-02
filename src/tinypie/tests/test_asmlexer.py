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


class AssemblerLexerTestCase(unittest.TestCase):

    def _get_token(self, text):
        from tinypie.lexer import AssemblerLexer
        lexer = AssemblerLexer(text)

        return lexer.token()

    def test_id(self):
        token = self._get_token('obj_id')
        self.assertEquals(token.type, tokens.ID)

    def test_int(self):
        token = self._get_token('777')
        self.assertEquals(token.type, tokens.INT)

    def test_string(self):
        token = self._get_token("'str'")
        self.assertEquals(token.type, tokens.STRING)

    def test_comma(self):
        token = self._get_token(' , ')
        self.assertEquals(token.type, tokens.COMMA)

    def test_colon(self):
        token = self._get_token(':')
        self.assertEquals(token.type, tokens.COLON)

    def test_assign(self):
        token = self._get_token('=')
        self.assertEquals(token.type, tokens.ASSIGN)

    def test_nl_return(self):
        token = self._get_token('\r\n')
        self.assertEquals(token.type, tokens.NL)

    def test_nl(self):
        token = self._get_token(' \n')
        self.assertEquals(token.type, tokens.NL)

    def test_def(self):
        token = self._get_token('.def')
        self.assertEquals(token.type, tokens.DEF)

    def test_globals(self):
        token = self._get_token('.globals')
        self.assertEquals(token.type, tokens.GLOBALS)

    def test_locals(self):
        token = self._get_token('locals')
        self.assertEquals(token.type, tokens.LOCALS)

    def test_args(self):
        token = self._get_token('args')
        self.assertEquals(token.type, tokens.ARGS)

    def test_call(self):
        token = self._get_token('call')
        self.assertEquals(token.type, tokens.CALL)

    def test_reg(self):
        token = self._get_token('r14')
        self.assertEquals(token.type, tokens.REG)

    def test_loadk(self):
        token = self._get_token('loadk')
        self.assertEquals(token.type, tokens.LOADK)
