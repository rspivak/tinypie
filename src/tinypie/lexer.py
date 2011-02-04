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

import re

from tinypie import tokens


class Token(object):

    def __init__(self, type, text=''):
        self.type = type
        self.text = text

    def __str__(self):
        return "<'{text}', {name}>".format(text=self.text, name=self.type)

    def __eq__(self, other):
        return self.type == other.type and self.text == other.text


class LexerException(Exception):

    def __init__(self, msg, pos):
        self.msg = msg
        self.pos = pos

    def __str__(self):
        return 'Error at position: %s - %s' % (self.pos, self.msg)


class Lexer(object):

    RULES = [
        (r'def', tokens.DEF),
        (r'\r?\n', tokens.NL),
        (r'print', tokens.PRINT),
        (r'return', tokens.RETURN),
        (r'if', tokens.IF),
        (r'else', tokens.ELSE),
        (r'while', tokens.WHILE),
        (r'[a-zA-Z_]+\d*', tokens.ID),
        (r'\d+', tokens.INT),
        (r"'[^']*'", tokens.STRING),
        (r'\(', tokens.LPAREN),
        (r'\)', tokens.RPAREN),
        (r'\.', tokens.DOT),
        (r',', tokens.COMMA),
        (r':', tokens.COLON),
        (r'==', tokens.EQ),
        (r'<', tokens.LT),
        (r'\+', tokens.ADD),
        (r'-', tokens.SUB),
        (r'\*', tokens.MUL),
        (r'=', tokens.ASSIGN),
        ]

    IS_WHITESPACE = re.compile(r'( |\t)+').match
    IS_COMMENT = re.compile(r'#.*').match

    def __init__(self, buffer):
        self.buffer = buffer
        self.pos = 0
        self.regexp = self._build_master_regexp()

    def _build_master_regexp(self):
        result = []
        for regexp, group_name in self.RULES:
            result.append(r'(?P<%s>%s)' % (group_name, regexp))

        master_regexp = re.compile('|'.join(result), re.MULTILINE)
        return master_regexp

    def token(self):
        buffer, regexp = self.buffer, self.regexp
        IS_WHITESPACE = self.IS_WHITESPACE
        IS_COMMENT = self.IS_COMMENT
        end = len(buffer)

        while True:
            match = (IS_WHITESPACE(buffer, self.pos) or
                     IS_COMMENT(buffer, self.pos))

            if match is not None:
                self.pos = match.end()
            else:
                break

        # the end
        if self.pos >= end:
            return Token(tokens.EOF, 'EOF')

        match = regexp.match(buffer, self.pos)
        if match is None:
            raise LexerException('No valid token', self.pos)

        self.pos = match.end()

        group_name = match.lastgroup
        token = Token(group_name, match.group(group_name))
        if token.type == tokens.STRING:
            token.text = token.text.strip("'")
        return token

    def __iter__(self):
        return self.next()

    def next(self):
        while True:
            token = self.token()
            if tokens.type == tokens.EOF:
                yield token
                return
            yield token


class AssemblerLexer(Lexer):

    RULES = [
        (r'\.globals', tokens.GLOBALS),
        (r'args', tokens.ARGS),
        (r'locals', tokens.LOCALS),
        (r'call', tokens.CALL),
        (r'loadk', tokens.LOADK),
        (r'r\d+', tokens.REG),
        (r'\.def', tokens.DEF),
        (r'\d+', tokens.INT),
        (r"'[^']*'", tokens.STRING),
        (r'\r?\n', tokens.NL),
        (r'[a-zA-Z_]+\d*', tokens.ID),
        (r',', tokens.COMMA),
        (r':', tokens.COLON),
        (r'=', tokens.ASSIGN),
        ]
