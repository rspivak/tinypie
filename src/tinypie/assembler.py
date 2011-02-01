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
from tinypie.parser import BaseParser
from tinypie.bytecode import INSTRUCTIONS


def write_int(code, address, value):
    # ensure capacity
    if address >= len(code):
        code.extend([0] * (len(code) - address + 4))

    code[address + 0] = (value >> (8 * 3)) & 0xff
    code[address + 1] = (value >> (8 * 2)) & 0xff
    code[address + 2] = (value >> 8) & 0xff
    code[address + 3] = value & 0xff


class LabelSymbol(object):

    def __init__(self, name, address=None, forward=False):
        self.name = name
        self.address = address
        self.forward = forward
        self.defined = False
        self.forward_refs = []

    def add_forward_ref(self, address):
        self.forward_refs.append(address)

    def resolve_forward_refs(self, code):
        for ref in self.forward_refs:
            write_int(code, ref, self.address)

class FunctionSymbol(object):

    def __init__(self, name, address, args, locals):
        self.name = name
        self.address = address
        self.args = args
        self.locals = locals


# program -> globals? (label | function_definition | instruction | NL)+
# globals -> '.globals' INT NL
# label -> ID ':' NL
# function_definition -> '.def' ID ':' 'args' '=' INT ',' 'locals' '=' INT NL
# instruction -> ID NL
#              | ID operand NL
#              | ID operand ',' operand NL
#              | ID operand ',' operand NL ',' operand NL
#              | 'call' operand
# operand -> REG | ID | STRING | INT

class BytecodeAssembler(BaseParser):
    """TinyPie Bytecode Assembler.

    It's a simple Syntax-Directed Translator that translates
    TinyPie assembly text into bytecode suitable for interpretation by
    TinyPie register-based VM (bytecode interpreter).
    """

    def __init__(self, lexer, lookahead_limit=2):
        self.lexer = lexer
        self.lookahead = [None] * lookahead_limit
        self.lookahead_limit = lookahead_limit
        self.pos = 0
        self._init_lookahead()
        self.global_size = 0
        self.code = bytearray()
        self.ip = 0
        self.constant_pool = []
        self.labels = {}
        self.main_function = None
        self.opcodes = dict(
            (instr.name, index + 1)
            for index, instr in enumerate(INSTRUCTIONS[1:])
            )

    def parse(self):

        while self._lookahead_type(0) != tokens.EOF:

            token_type = self._lookahead_type(0)

            if token_type == tokens.NL:
                self._match(tokens.NL)

            elif token_type == tokens.GLOBALS:
                self._globals()

            elif token_type == tokens.DEF:
                self._func_def()

            elif (token_type == tokens.ID and
                  self._lookahead_type(1) == tokens.COLON
                  ):
                self._label()

            else:
                self._instruction()

    def _globals(self):
        """Globals rule.

        globals -> '.globals' INT NL
        """
        self._match(tokens.GLOBALS)

        token = self._lookahead_token(0)
        self.global_size = int(token.text)
        self._match(tokens.INT)
        self._match(tokens.NL)

    def _func_def(self):
        """Function definition rule.

        function_definition ->
            '.def' ID ':' 'args' '=' INT ',' 'locals' '=' INT NL
        """

        self._match(tokens.DEF)

        name = self._lookahead_token(0).text
        self._match(tokens.ID)

        self._match(tokens.COLON)

        self._match(tokens.ARGS)
        self._match(tokens.ASSIGN)
        args = int(self._lookahead_token(0).text)
        self._match(tokens.INT)

        self._match(tokens.COMMA)

        self._match(tokens.LOCALS)
        self._match(tokens.ASSIGN)
        locals_num = int(self._lookahead_token(0).text)
        self._match(tokens.INT)

        self._match(tokens.NL)

        func_sym = FunctionSymbol(name, self.ip, args, locals_num)
        if name == 'main':
            self.main_function = func_sym

        if func_sym not in self.constant_pool:
            self.constant_pool.append(func_sym)

    def _label(self):
        """Label rule.

        label -> ID ':' NL
        """
        token = self._lookahead_token(0)
        self._define_label(token.text)
        self._match(tokens.ID)
        self._match(tokens.COLON)
        self._match(tokens.NL)

    def _instruction(self):
        """Instruction rule.

        instruction -> ID NL
                     | ID operand NL
                     | ID operand ',' operand NL
                     | ID operand ',' operand ',' operand NL
                     | 'call' operand ',' operand NL
        """
        token = self._lookahead_token(0)
        opcode = self._gen(token)
        self._match(tokens.ID)

        if self._lookahead_type(0) == tokens.NL:
            self._match(tokens.NL)
            return

        token = self._lookahead_token(0)
        self._operand()
        self._gen_operand(token)
        if self._lookahead_type(0) == tokens.NL:
            self._match(tokens.NL)
            return

        self._match(tokens.COMMA)
        token = self._lookahead_token(0)
        self._operand()
        self._gen_operand(token)
        if self._lookahead_type(0) == tokens.NL:
            self._match(tokens.NL)
            return

        self._match(tokens.COMMA)
        token = self._lookahead_token(0)
        self._operand()
        self._gen_operand(token)
        self._match(tokens.NL)

    def _operand(self):
        """Operand rule.

        operand -> REG | ID | STRING | INT
        """
        self._match(self._lookahead_type(0))

    # Helper method
    def _gen(self, instr_token):
        opcode = self.opcodes[instr_token.text]
        self.code.append(opcode & 0xff)
        self.ip += 1

    def _gen_operand(self, token):
        value = {
            tokens.INT: lambda: int(token.text),
            tokens.STRING: lambda: self._get_constant_pool_index(token.text),
            tokens.ID: lambda: self._get_label_address(token.text),
            tokens.REG: lambda: self._get_reg_number(token.text),
            }.get(token.type)()

        write_int(self.code, self.ip, value)
        self.ip += 4

    def _get_reg_number(self, text):
        return int(text[1:])

    def _get_label_address(self, name):
        label = self.labels.get(name)

        if label is None:
            # add forward reference
            label = LabelSymbol(name, forward=True)
            self.labels[label.name] = label
            label.add_forward_ref(self.ip)

        else:

            if label.forward:
                label.add_forward_ref(self.ip)

            else:
                return label.address

        return 0

    def _define_label(self, name):
        label = self.labels.get(name)
        if label is None:
            label = LabelSymbol(name, self.ip)
            self.labels[name] = label

        label.address = self.ip
        label.defined = True
        label.forward = False
        label.resolve_forward_refs(self.code)
