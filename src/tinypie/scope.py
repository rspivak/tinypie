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


class Scope(object):

    def get_enclosing_scope(self):
        raise NotImplementedError

    def define(self, symbol):
        raise NotImplementedError

    def resolve(self, name):
        raise NotImplementedError


class BaseScope(Scope):

    def __init__(self, enclosing_scope):
        self.enclosing_scope = enclosing_scope
        self.symbols = {}

    def get_enclosing_scope(self):
        return self.enclosing_scope

    def define(self, symbol):
        self.symbols[symbol.name] = symbol
        symbol.scope = self

    def resolve(self, name):
        symbol = self.symbols.get(name)
        if symbol is not None:
            return symbol

        if self.get_enclosing_scope() is not None:
            return self.get_enclosing_scope().resolve(name)


class LocalScope(BaseScope):

    @property
    def name(self):
        return 'local'


class GlobalScope(BaseScope):

    def __init__(self):
        super(GlobalScope, self).__init__(None)

    @property
    def name(self):
        return 'global'
