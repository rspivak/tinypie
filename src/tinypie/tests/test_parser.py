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
        from tinypie.scope import GlobalScope

        class Interpreter(object):
            global_scope = GlobalScope()

        parser = Parser(Lexer(text), interpreter=Interpreter())
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


class ASTTestCase(unittest.TestCase):

    def _get_parser(self, text):
        from tinypie.lexer import Lexer
        from tinypie.parser import Parser
        from tinypie.scope import GlobalScope

        class Interpreter(object):
            global_scope = GlobalScope()

        parser = Parser(Lexer(text), interpreter=Interpreter())
        return parser

    def _compare_tree(self, expected_node, node):
        self.assertEquals(expected_node, node,
                          'expected: %s - got: %s' % (expected_node, node))
        self.assertEquals(len(expected_node.children), len(node.children))

        for child1, child2 in zip(expected_node.children, node.children):
            self._compare_tree(child1, child2)

    def test_function_definition(self):
        from tinypie.ast import AST
        from tinypie.lexer import Token
        from tinypie import tokens

        text = """
        def foo(x) print x
        """
        parser = self._get_parser(text)
        parser.parse()

        tree = AST(tokens.BLOCK)

        func_node = AST(tokens.FUNC_DEF)
        func_node.add_child(AST(Token(tokens.ID, 'foo')))
        func_node.add_child(AST(Token(tokens.ID, 'x')))

        block_node = AST(tokens.BLOCK)
        print_node = AST(Token(tokens.PRINT, 'print'))
        print_node.add_child(AST(Token(tokens.ID, 'x')))
        block_node.add_child(print_node)
        func_node.add_child(block_node)

        tree.add_child(func_node)

        self._compare_tree(tree, parser.root)

    def test_print(self):
        from tinypie.ast import AST
        from tinypie.lexer import Token
        from tinypie import tokens

        text = """
        print x
        """
        parser = self._get_parser(text)
        parser.parse()

        tree = AST(tokens.BLOCK)
        print_node = AST(Token(tokens.PRINT, 'print'))
        print_node.add_child(AST(Token(tokens.ID, 'x')))
        tree.add_child(print_node)

        self._compare_tree(tree, parser.root)

    def test_return(self):
        from tinypie.ast import AST
        from tinypie.lexer import Token
        from tinypie import tokens

        text = """
        return x
        """
        parser = self._get_parser(text)
        parser.parse()

        tree = AST(tokens.BLOCK)
        return_node = AST(Token(tokens.RETURN, 'return'))
        return_node.add_child(AST(Token(tokens.ID, 'x')))
        tree.add_child(return_node)

        self._compare_tree(tree, parser.root)

    def test_call(self):
        from tinypie.ast import AST
        from tinypie.lexer import Token
        from tinypie import tokens

        text = """
        foo(5)
        """
        parser = self._get_parser(text)
        parser.parse()

        tree = AST(tokens.BLOCK)
        call_node = AST(Token(tokens.CALL))
        call_node.add_child(AST(Token(tokens.ID, 'foo')))
        call_node.add_child(AST(Token(tokens.INT, '5')))
        tree.add_child(call_node)

        self._compare_tree(tree, parser.root)

    def test_while(self):
        from tinypie.ast import AST
        from tinypie.lexer import Token
        from tinypie import tokens

        text = """
        while x < 10:
            print x
        .
        """
        parser = self._get_parser(text)
        parser.parse()

        tree = AST(tokens.BLOCK)
        while_node = AST(Token(tokens.WHILE, 'while'))

        lt_node = AST(Token(tokens.LT, '<'))
        lt_node.add_child(AST(Token(tokens.ID, 'x')))
        lt_node.add_child(AST(Token(tokens.INT, '10')))
        while_node.add_child(lt_node)

        block_node = AST(tokens.BLOCK)
        print_node = AST(Token(tokens.PRINT, 'print'))
        print_node.add_child(AST(Token(tokens.ID, 'x')))
        block_node.add_child(print_node)
        while_node.add_child(block_node)

        tree.add_child(while_node)

        self._compare_tree(tree, parser.root)

    def test_ifstat(self):
        from tinypie.ast import AST
        from tinypie.lexer import Token
        from tinypie import tokens

        text = """
        if x < 10 print x
        else print 'less'
        """
        parser = self._get_parser(text)
        parser.parse()

        tree = AST(tokens.BLOCK)
        ifstat_node = AST(Token(tokens.IF, 'if'))

        lt_node = AST(Token(tokens.LT, '<'))
        lt_node.add_child(AST(Token(tokens.ID, 'x')))
        lt_node.add_child(AST(Token(tokens.INT, '10')))
        ifstat_node.add_child(lt_node)

        block_node = AST(tokens.BLOCK)
        print_node = AST(Token(tokens.PRINT, 'print'))
        print_node.add_child(AST(Token(tokens.ID, 'x')))
        block_node.add_child(print_node)
        ifstat_node.add_child(block_node)

        block_node = AST(tokens.BLOCK)
        print_node = AST(Token(tokens.PRINT, 'print'))
        print_node.add_child(AST(Token(tokens.STRING, 'less')))
        block_node.add_child(print_node)
        ifstat_node.add_child(block_node)

        tree.add_child(ifstat_node)

        self._compare_tree(tree, parser.root)
