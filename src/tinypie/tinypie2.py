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

import ply.lex as lex
import ply.yacc as yacc

# Example:
# tinypie > x = 7
# tinypie > print x
# tinypie > print 5
#
# Grammar
# program   -> (statement)+
# statement -> print
#            | assign
# print     -> PRINT INT
#            | PRINT ID
# assign    -> ID '=' INT

# Symbol table / Monolithic scope / Global scope
NAMES = {}

tokens = ['PRINT', 'ID', 'INT']

literals = ['=']

# Tokens
def t_PRINT(t):
    r"""print"""
    return t

digit = r'([0-9])'
nondigit = r'([_A-Za-z])'
identifier = r'(' + nondigit + r'(' + digit + r'|' + nondigit + r')*)'

@lex.TOKEN(identifier)
def t_ID(t):
    return t

def t_INT(t):
    r"""\d+"""
    t.value = int(t.value)
    return t

t_ignore = ' \t'

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Parsing rules
def p_program(p):
    """program : statement"""
    p[0] = p[1]

def p_statement(p):
    """statement : print
                 | assign
    """
    p[0] = p[1]

def p_print(p):
    """print : PRINT ID
             | PRINT INT
    """
    p[0] = PrintNode(p[2])

def p_assign(p):
    """assign : ID '=' INT"""
    left, right = p[1], p[3]
    NAMES[left] = right

def p_error(p):
    print "Syntax error at '%s'" % t.value

# AST
class PrintNode(object):
    def __init__(self, value):
        self.value = value

class NodeVisitor(object):
    def visit(self, node):
        method = 'visit_%s' % node.__class__.__name__
        return getattr(self, method, self.generic_visit)(node)

    def generic_visit(self, node):
        return 'GEN: %r' % node

    def visit_PrintNode(self, node):
        value = node.value
        if value in NAMES:
            print NAMES[value] # print x
        elif isinstance(value, int):
            print value        # print 5
        else:
            print 'Could not resolve the symbol: %s' % value

# Start the parser
lex.lex()
yacc.yacc()
visitor = NodeVisitor()

while True:
    try:
        line = raw_input('tinypie > ')
    except EOFError:
        break
    if not line:
        continue
    tree = yacc.parse(line)
    visitor.visit(tree)
