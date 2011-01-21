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

    def __init__(self, func_symbol):
        super(FunctionSpace, self).__init__(func_symbol.name)
        self.func_symbol = func_symbol


class ReturnValue(Exception):

    def __init__(self, *args, **kwargs):
        self.value = kwargs.pop('value')


class InterpreterException(Exception):
    pass


class Interpreter(object):
    """Tree-Based Interpreter class.

    Executes code by constructing AST and walking the tree.
    """

    def __init__(self):
        self.global_scope = GlobalScope()
        self.globals = MemorySpace('global')
        self.func_stack = []
        self.current_space = self.globals

    def interpret(self, text):
        """Interprete passed source code."""
        parser = Parser(Lexer(text), interpreter=self)
        parser.parse()
        tree = parser.root
        self._block(tree)

    def _exec(self, node):
        """Dispatch method of external tree visitor"""

        if node.type == tokens.BLOCK:
            self._block(node)

        elif node.type == tokens.RETURN:
            self._ret(node)

        elif node.type == tokens.CALL:
            return self._call(node)

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

        elif node.type in (tokens.ADD, tokens.SUB, tokens.MUL):
            return self._binop(node)

        elif node.type in (tokens.LT, tokens.EQ):
            return self._compare(node)

        elif node.type == tokens.IF:
            self._ifstat(node)

        elif node.type == tokens.WHILE:
            self._whileop(node)

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

    def _call(self, node):
        func_name = node.children[0].text
        func_symbol = node.scope.resolve(func_name)
        func_space = FunctionSpace(func_symbol)
        save_space = self.current_space
        self.current_space = func_space

        for index, arg in enumerate(func_symbol.formal_args):
            name = arg.name
            value = self._exec(node.children[index + 1])
            self.current_space.put(name, value)

        # push local scope
        self.func_stack.append(func_space)

        try:
            self._exec(func_symbol.block_ast)
        except ReturnValue as rv:
            return rv.value
        finally:
            self.func_stack.pop()
            self.current_space = save_space

    def _binop(self, node):
        left = self._exec(node.children[0])
        right = self._exec(node.children[1])

        if node.type == tokens.ADD:
            return left + right

        if node.type == tokens.SUB:
            return left - right

        if node.type == tokens.MUL:
            return left * right

    def _compare(self, node):
        left = self._exec(node.children[0])
        right = self._exec(node.children[1])

        if node.type == tokens.LT:
            return left < right

        if node.type == tokens.EQ:
            return left == right

    def _load(self, node):
        name = node.text
        memory_space = self._get_symbol_space(name)
        if memory_space is not None:
            return memory_space.get(name)

        raise InterpreterException("name '%s' is not defined" % name)

    def _ifstat(self, node):
        cond_predicate = node.children[0]
        cond_consequent = node.children[1]
        cond_else = node.children[2] if len(node.children) == 3 else None

        if self._exec(cond_predicate):
            self._exec(cond_consequent)

        elif cond_else is not None:
            self._exec(cond_else)

    def _whileop(self, node):
        cond_start = node.children[0]
        code_start = node.children[1]
        cond = self._exec(cond_start)
        while cond:
            self._exec(code_start)
            cond = self._exec(cond_start)

    def _get_symbol_space(self, name):
        if self.func_stack and name in self.func_stack[-1]:
            return self.func_stack[-1]

        if name in self.globals:
            return self.globals

        return None


def main():
    if len(sys.argv) != 2:
        print 'Usage: tinypie input_file'
        sys.exit(1)

    interp = Interpreter()
    text = open(sys.argv[1]).read()
    interp.interpret(text)
