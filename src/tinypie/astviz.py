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

from jinja2 import Template

from tinypie.lexer import Lexer
from tinypie.parser import Parser
from tinypie.scope import GlobalScope


DOT_TEMPLATE = """\
digraph astgraph {
   node [shape=plaintext, fontsize=12, fontname="Courier", height=.1];
   ranksep=.3;
   edge [arrowsize=.5]

{% for node in nodes %}\
   {{ node }}
{% endfor %}
{% for edge in edges %}\
   {{ edge }}
{% endfor %}\
}
"""

NODE_TEMPLATE = '{{ name }} [label="{{ text }}"];'

EDGE_TEMPLATE = '{{ from }} -> {{ to }}'


class ASTVisualizer(object):
    """DOT generator.

    Generates DOT commands by walking the AST tree and using
    Jinja2 templates as a DSL for output generation.

    Example usage:

    >>> from tinypie.lexer import Lexer
    >>> from tinypie.parser import Parser
    >>> from tinypie.scope import GlobalScope
    >>> from tinypie.astviz import ASTVisualizer
    >>>
    >>> class Interpreter(object):
    ...     def __init__(self):
    ...         self.global_scope = GlobalScope()
    ...
    >>> source = 'foo(3, 7)\n'
    >>> parser = Parser(Lexer(source), interpreter=Interpreter())
    >>> parser.parse()
    >>> tree = parser.root
    >>> visualizer = ASTVisualizer(tree)
    >>> print visualizer
    digraph astgraph {
       node [shape=plaintext, fontsize=12, fontname="Courier", height=.1];
       ranksep=.3;
       edge [arrowsize=.5]
    <BLANKLINE>
       node1 [label="BLOCK"];
       node2 [label="CALL"];
       node3 [label="ID (foo)"];
       node4 [label="INT (3)"];
       node5 [label="INT (7)"];
    <BLANKLINE>
       node2 -> node3
       node2 -> node4
       node2 -> node5
       node1 -> node2
    }

    """

    def __init__(self, tree):
        self.tree = tree
        self.count = 1

    def __str__(self):
        self.count = 1

        def _render_templates(values):
            return [template.render(context) for template, context in values]

        nodes, edges = [], []
        self.walk(self.tree, nodes, edges)
        template = Template(DOT_TEMPLATE)
        output = template.render(
            nodes=_render_templates(nodes), edges=_render_templates(edges))

        return output

    def walk(self, node, nodes, edges):
        result = parent_tmpl, parent_context = self._get_node_template(node)
        nodes.append(result)

        for child in node.children:
            _, child_context = self.walk(child, nodes, edges)
            from_text = parent_context['name']
            to_text = child_context['name']
            edges.append(self._get_edge_template(from_text, to_text))

        return (parent_tmpl, parent_context)

    def _get_node_template(self, node):
        payload, text = node.type, node.text
        if text:
            payload = '%s (%s)' % (payload, text)
        template = Template(NODE_TEMPLATE)
        context = {'name': 'node%s' % self.count, 'text': payload}
        self.count += 1
        return (template, context)

    @staticmethod
    def _get_edge_template(from_text, to_text):
        template = Template(EDGE_TEMPLATE)
        return template, {'from': from_text, 'to': to_text}


class Interpreter(object):
    """Stub"""

    def __init__(self):
        self.global_scope = GlobalScope()


def generate_dot():
    """Read source code, generate DOT file, and print it to STDOUT.

    If source file name is not provided on the command line
    defaults to STDIN.
    """
    if len(sys.argv) != 2:
        source = sys.stdin.read()
    else:
        source = open(sys.argv[1]).read()

    parser = Parser(Lexer(source), interpreter=Interpreter())
    parser.parse()
    visualizer = ASTVisualizer(parser.root)
    print visualizer


if __name__ == '__main__':
    generate_dot()
