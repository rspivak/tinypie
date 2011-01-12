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

from tinypie import tokens

# program             -> (function_definition | statement)+ EOF
# function_definition -> 'def' ID '(' (ID (',' ID)*)? ')' slist
# slist               -> ':' NL statement+ '.' NL
#                        | statement
# statement           -> 'print' expr NL
#                        | 'return' expr NL
#                        | call NL
#                        | assign NL
#                        | 'if' expr slist ('else' slist)?
#                        | 'while' expr slist
#                        | NL
# assign              -> ID '=' expr
# expr                -> add_expr (('<' | '==') add_expr)?
# add_expr            -> mult_expr (('+' | '-') mult_expr)*
# mult_expr           -> atom ('*' atom)*
# atom                -> ID | INT | STRING | call | '(' expr ')'
# call                -> ID '(' (expr (',' expr)*)? ')'


class ParserException(Exception):
    pass


class Parser(object):
    """TinyPie Parser"""

    def __init__(self, lexer, lookahead_limit=2):
        self.lexer = lexer
        self.lookahead = [None] * lookahead_limit
        self.lookahead_limit = lookahead_limit
        self.pos = 0
        self._init_lookahead()

    def parse(self):
        while self._lookahead_type(0) != tokens.EOF:

            token_type = self._lookahead_type(0)

            if token_type == tokens.DEF:
                self._function_definition()
            else:
                self._statement()

    def _function_definition(self):
        """Function definition rule.

        function_definition -> 'def' ID '(' (ID (',' ID)*)? ')' slist
        """
        self._match(tokens.DEF)
        self._match(tokens.ID)
        self._match(tokens.LPAREN)

        if self._lookahead_type(0) == tokens.ID:
            self._match(tokens.ID)

            while self._lookahead_type(0) == tokens.COMMA:
                self._match(tokens.COMMA)
                self._match(tokens.ID)

        self._match(tokens.RPAREN)
        self._slist()

    def _slist(self):
        """Statement list rule.

        slist -> ':' NL statement+ '.' NL
                 | statement
        """
        if self._lookahead_type(0) == tokens.COLON:
            self._match(tokens.COLON)
            self._match(tokens.NL)

            while (self._lookahead_type(0) != tokens.DOT and
                   self._lookahead_type(1) != tokens.NL
                   ):
                self._statement()

            self._match(tokens.DOT)
            self._match(tokens.NL)

        else:
            self._statement()

    def _statement(self):
        """Statement rule.

        statement -> 'print' expr NL
                     | 'return' expr NL
                     | call NL
                     | assign NL
                     | 'if' expr slist ('else' slist)?
                     | 'while' expr slist
                     | NL
        """
        if self._lookahead_type(0) == tokens.PRINT:
            self._match(tokens.PRINT)
            self._expr()
            self._match(tokens.NL)

        elif self._lookahead_type(0) == tokens.RETURN:
            self._match(tokens.RETURN)
            self._expr()
            self._match(tokens.NL)

        elif self._lookahead_type(0) == tokens.NL:
            self._match(tokens.NL)

    def _expr(self):
        """Expression rule.

        expr -> add_expr (('<' | '==') add_expr)?
        """
        self._add_expr()

        if self._lookahead_type(0) == tokens.LT:
            self._match(tokens.LT)
            self._add_expr()

        elif self._lookahead_type(0) == tokens.EQ:
            self._match(tokens.EQ)
            self._add_expr()

    def _add_expr(self):
        """Add expression rule.

        add_expr -> mult_expr (('+' | '-') mult_expr)*
        """

        self._mult_expr()

        while self._lookahead_type(0) in (tokens.ADD, tokens.SUB):
            if self._lookahead_type(0) == tokens.ADD:
                self._match(tokens.ADD)
                self._mult_expr()

            elif self._lookahead_type(0) == tokens.SUB:
                self._match(tokens.SUB)
                self._mult_expr()

    def _mult_expr(self):
        """Multiply expression rule.

        mult_expr -> atom ('*' atom)*
        """
        self._atom()

        while self._lookahead_type(0) == tokens.MUL:
            self._match(tokens.MUL)
            self._atom()

    def _assign(self):
        """Assign rule.

        assign -> ID '=' expr
        """
        pass

    def _call(self):
        """Call rule.

        call -> ID '(' (expr (',' expr)*)? ')'
        """
        pass

    def _atom(self):
        """Atom rule.

        atom -> ID | INT | STRING | call | '(' expr ')'
        """
        if (self._lookahead_type(0) == tokens.ID and
              self._lookahead_type(0) == tokens.LPAREN
              ):
            self._call()

        elif self._lookahead_type(0) == tokens.ID:
            self._match(tokens.ID)

        elif self._lookahead_type(0) == tokens.INT:
            self._match(tokens.INT)

        elif self._lookahead_type(0) == tokens.STRING:
            self._match(tokens.STRING)

        elif self._lookahead_type(0) == tokens.LPAREN:
            self._match(tokens.LPAREN)
            self._expr()
            self._match(tokens.RPAREN)

    # Helper methods
    def _init_lookahead(self):
        for _ in range(self.lookahead_limit):
            self._consume()

    def _match(self, token_type):
        if self._lookahead_type(0) == token_type:
            self._consume()
        else:
            raise ParserException(
                'Expecting %s; found %s' % (
                    token_type, self._lookahead_token(0))
                )

    def _consume(self):
        self.lookahead[self.pos] = self.lexer.token()
        self.pos = (self.pos + 1) % self.lookahead_limit

    def _lookahead_type(self, number):
        return self._lookahead_token(number).type

    def _lookahead_token(self, number):
        return self.lookahead[(self.pos + number) % self.lookahead_limit]
