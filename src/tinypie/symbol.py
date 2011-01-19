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

from tinypie.scope import Scope


class Symbol(object):

    def __init__(self, name):
        self.name = name
        self.scope = None


class VariableSymbol(Symbol):
    pass


class ScopedSymbol(Scope, Symbol):

    def __init__(self, name, enclosing_scope):
        super(ScopedSymbol, self).__init__(name)
        self.enclosing_scope = enclosing_scope


class FunctionSymbol(ScopedSymbol):

    def __init__(self, name, enclosing_scope):
        super(FunctionSymbol, self).__init__(name, enclosing_scope)
        # self.formal_args = None
        self.block_ast = None
        self.symbols = {}
        self.ordered_symbols = []

    @property
    def formal_args(self):
        return self.ordered_symbols

    def get_enclosing_scope(self):
        return self.enclosing_scope

    def define(self, symbol):
        self.symbols[symbol.name] = symbol
        symbol.scope = self
        self.ordered_symbols.append(symbol)

    def resolve(self, name):
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol

        if self.get_enclosing_scope() is not None:
            return self.get_enclosing_scope().resolve(name)
