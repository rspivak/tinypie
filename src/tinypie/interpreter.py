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

from tinypie.lexer import Lexer
from tinypie.parser import Parser
from tinypie.scope import GlobalScope
from tinypie import tokens


class MemorySpace(object):

    def __init__(self, name):
        self.name = name
        self.members = {}

    def __contains__(self, key):
        return key in self.members

    def get(self, name):
        return self.members.get(name)

    def put(self, name, value):
        self.members[name] = value


class FunctionSpace(MemorySpace):
    pass


class ReturnValue(Exception):

    def __init__(self, *args, **kwargs):
        self.value = kwargs.pop('value')


class Interpreter(object):

    def __init__(self):
        self.global_scope = GlobalScope()
        self.globals = MemorySpace('global')
        self.func_stack = []
        self.current_space = self.globals

    def interpret(self, text):
        parser = Parser(Lexer(text), interpreter=self)
        parser.parse()
        tree = parser.root
        self._block(tree)

    def _exec(self, node):

        if node.type == tokens.BLOCK:
            self._block(node)

        elif node.type == tokens.RETURN:
            self._ret(node)

        elif node.type == tokens.CALL:
            self._call(node)

        elif node.type == tokens.ASSIGN:
            self._assign(node)

        elif node.type == tokens.PRINT:
            self._print(node)

        elif node.type == tokens.INT:
            return int(node.text)

        elif node.type == tokens.STRING:
            return node.text

        elif node.type == tokens.ID:
            return self._load(node)

    def _block(self, node):
        for child in node.children:
            self._exec(child)

    def _ret(self, node):
        raise ReturnValue(value=self._exec(node.children[0]))

    def _assign(self, node):
        left = node.children[0]
        value = self._exec(node.children[1])

        memory_space = self._get_symbol_space(left.text)
        if memory_space is None:
            memory_space = self.current_space

        memory_space.put(left.text, value)

    def _print(self, node):
        value = self._exec(node.children[0])
        print value

    def _load(self, node):
        name = node.text
        memory_space = self._get_symbol_space(name)
        if memory_space is not None:
            return memory_space.get(name)
        return None

    def _get_symbol_space(self, name):
        if self.func_stack and name in self.func_stack[-1]:
            return self.func_stack[-1]

        if name in self.globals:
            return self.globals

        return None


def main():
    pass
