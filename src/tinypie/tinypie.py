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
# tinypie > print 5
#
# Grammar
# program -> PRINT INT

tokens = ['PRINT', 'INT']

# Tokens
t_ignore = ' \t'
t_PRINT = r'print'

def t_INT(t):
    r"""\d+"""
    t.value = int(t.value)
    return t

def t_error(t):
    print "Illegal character '%s'" % t.value[0]
    t.lexer.skip(1)

# Parsing rules
def p_program(p):
    """program : PRINT INT"""
    p[0] = PrintNode(p[2])

def p_error(p):
    print "Syntax error at '%s'" % p.value

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
        print node.value

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
