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
from tinypie.ast import AST
from tinypie.scope import LocalScope
from tinypie.symbol import VariableSymbol, FunctionSymbol

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


class BaseParser(object):

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


class Parser(BaseParser):
    """TinyPie Parser"""

    def __init__(self, lexer, lookahead_limit=2, interpreter=None):
        self.lexer = lexer
        self.lookahead = [None] * lookahead_limit
        self.lookahead_limit = lookahead_limit
        self.pos = 0
        self._init_lookahead()
        self.root = AST(tokens.BLOCK)
        self.current_node = self.root
        self.interpreter = interpreter
        self.current_scope = interpreter.global_scope

    def parse(self):
        node = AST(tokens.BLOCK)

        while self._lookahead_type(0) != tokens.EOF:

            token_type = self._lookahead_type(0)

            if token_type == tokens.DEF:
                node.add_child(self._function_definition())
            else:
                st_node = self._statement()
                if st_node is not None:
                    node.add_child(st_node)

        self.root = node

    def _function_definition(self):
        """Function definition rule.

        function_definition -> 'def' ID '(' (ID (',' ID)*)? ')' slist
        """
        self._match(tokens.DEF)

        node = AST(tokens.FUNC_DEF)
        id_token = self._lookahead_token(0)
        node.add_child(AST(id_token))

        func_symbol = FunctionSymbol(id_token.text, self.current_scope)
        func_symbol.scope = self.current_scope
        self.current_scope.define(func_symbol)
        self.current_scope = func_symbol

        self._match(tokens.ID)
        self._match(tokens.LPAREN)

        if self._lookahead_type(0) == tokens.ID:
            node.add_child(AST(self._lookahead_token(0)))

            variable_symbol = VariableSymbol(self._lookahead_token(0).text)
            variable_symbol.scope = self.current_scope
            self.current_scope.define(variable_symbol)

            self._match(tokens.ID)

            while self._lookahead_type(0) == tokens.COMMA:
                self._match(tokens.COMMA)
                node.add_child(AST(self._lookahead_token(0)))

                variable_symbol = VariableSymbol(self._lookahead_token(0).text)
                self.current_scope.define(variable_symbol)
                variable_symbol.scope = self.current_scope

                self._match(tokens.ID)

        self._match(tokens.RPAREN)

        self.current_scope = LocalScope(self.current_scope)

        block_ast = self._slist()
        func_symbol.block_ast = block_ast
        node.add_child(block_ast)

        # pop LocalScope
        self.current_scope = self.current_scope.get_enclosing_scope()

        # pop FunctionSymbol
        self.current_scope = self.current_scope.get_enclosing_scope()

        return node

    def _slist(self):
        """Statement list rule.

        slist -> ':' NL statement+ '.' NL
                 | statement
        """
        node = AST(tokens.BLOCK)

        if self._lookahead_type(0) == tokens.COLON:
            self._match(tokens.COLON)
            self._match(tokens.NL)

            while not (self._lookahead_type(0) == tokens.DOT and
                       self._lookahead_type(1) == tokens.NL):
                st_node = self._statement()
                if st_node is not None:
                    node.add_child(st_node)

            self._match(tokens.DOT)
            self._match(tokens.NL)

        else:
            st_node = self._statement()
            if st_node is not None:
                node.add_child(st_node)

        return node

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
            node = AST(self._lookahead_token(0))
            self._match(tokens.PRINT)
            node.add_child(self._expr())
            self._match(tokens.NL)
            return node

        elif self._lookahead_type(0) == tokens.RETURN:
            node = AST(self._lookahead_token(0))
            self._match(tokens.RETURN)
            node.add_child(self._expr())
            self._match(tokens.NL)
            return node

        elif self._lookahead_type(0) == tokens.NL:
            self._match(tokens.NL)

        elif (self._lookahead_type(0) == tokens.ID and
              self._lookahead_type(1) == tokens.LPAREN
              ):
            return self._call()

        elif self._lookahead_type(0) == tokens.IF:
            node = AST(self._lookahead_token(0))
            self._match(tokens.IF)
            node.add_child(self._expr())
            node.add_child(self._slist())
            if self._lookahead_type(0) == tokens.ELSE:
                self._match(tokens.ELSE)
                node.add_child(self._slist())
            return node

        elif self._lookahead_type(0) == tokens.WHILE:
            node = AST(self._lookahead_token(0))
            self._match(tokens.WHILE)
            node.add_child(self._expr())
            node.add_child(self._slist())
            return node

        else:
            return self._assign()

    def _expr(self):
        """Expression rule.

        expr -> add_expr (('<' | '==') add_expr)?
        """
        left_node = self._add_expr()

        if self._lookahead_type(0) in (tokens.LT, tokens.EQ):
            node = AST(self._lookahead_token(0))
            node.add_child(left_node)
            self._match(self._lookahead_type(0))
            node.add_child(self._add_expr())
            left_node = node

        return left_node

    def _add_expr(self):
        """Add expression rule.

        add_expr -> mult_expr (('+' | '-') mult_expr)*
        """
        left_node = self._mult_expr()

        while self._lookahead_type(0) in (tokens.ADD, tokens.SUB):
            node = AST(self._lookahead_token(0))
            node.add_child(left_node)
            self._match(self._lookahead_type(0))
            node.add_child(self._mult_expr())
            left_node = node

        return left_node

    def _mult_expr(self):
        """Multiply expression rule.

        mult_expr -> atom ('*' atom)*
        """
        result_node = self._atom()

        while self._lookahead_type(0) == tokens.MUL:
            node = AST(self._lookahead_token(0))
            node.add_child(result_node)
            self._match(tokens.MUL)
            node.add_child(self._atom())
            result_node = node

        return result_node

    def _assign(self):
        """Assign rule.

        assign -> ID '=' expr
        """
        node = AST(tokens.ASSIGN)
        node.add_child(AST(self._lookahead_token(0)))

        variable_symbol = VariableSymbol(self._lookahead_token(0).text)
        variable_symbol.scope = self.current_scope
        self.current_scope.define(variable_symbol)

        self._match(tokens.ID)
        self._match(tokens.ASSIGN)
        node.add_child(self._expr())

        return node

    def _call(self):
        """Call rule.

        call -> ID '(' (expr (',' expr)*)? ')'
        """
        node = AST(tokens.CALL)
        node.scope = self.current_scope
        node.add_child(AST(self._lookahead_token(0)))

        self._match(tokens.ID)
        self._match(tokens.LPAREN)
        result_node = self._expr()
        if result_node is not None:
            node.add_child(result_node)

        while self._lookahead_type(0) == tokens.COMMA:
            self._match(tokens.COMMA)
            node.add_child(self._expr())
        self._match(tokens.RPAREN)

        return node

    def _atom(self):
        """Atom rule.

        atom -> ID | INT | STRING | call | '(' expr ')'
        """
        if (self._lookahead_type(0) == tokens.ID and
              self._lookahead_type(1) == tokens.LPAREN
              ):
            return self._call()

        elif self._lookahead_type(0) == tokens.ID:
            node = AST(self._lookahead_token(0))
            self._match(tokens.ID)
            return node

        elif self._lookahead_type(0) == tokens.INT:
            node = AST(self._lookahead_token(0))
            self._match(tokens.INT)
            return node

        elif self._lookahead_type(0) == tokens.STRING:
            # strip single quote around the string
            token = self._lookahead_token(0)
            token.text = token.text.strip("'")
            node = AST(token)
            self._match(tokens.STRING)
            return node

        elif self._lookahead_type(0) == tokens.LPAREN:
            self._match(tokens.LPAREN)
            node = self._expr()
            self._match(tokens.RPAREN)
            return node
