TinyPie - Tree-Based Interpreter for TinyPie language
=====================================================

Overview
--------

TinyPie is a tree-based interpreter for a simple programming
language with a Python-like syntax.

It's based on Pie language from [Language Implementation Patterns](http://pragprog.com/titles/tpdsl/language-implementation-patterns) Ch.9

Quote from [the book](http://pragprog.com/titles/tpdsl/language-implementation-patterns): "A tree-based interpreter is like a compiler front
end with an interpreter grafted onto the end instead of a code generator"


Goals of the project
--------------------

1. Self-education

2. To serve as an example for people interested in crafting
   their own interpreter in Python for a simple programming language or DSL


Installation
------------

1. Using `buildout`

        $ git clone git://github.com/rspivak/tinypie.git
        $ cd tinypie
        $ python bootstrap.py
        $ bin/buildout

        Run the interpreter

        $ bin/tinypie factorial.tp

2. Using `pip` or `easy_install` (no need for sudo if using `virtualenv`)

        $ sudo pip install tinypie

        (or run alternatively easy_install: $ sudo easy_install tinypie)

        Run the interpreter

        $ tinypie factorial.tp


Main interpreter features
-------------------------

- Implemented in Python

- Regexp-based lexer

- LL(k) recursive-descent parser

- Parser constructs homogeneous Abstract Syntax Tree (AST)

- Static / lexical scope support.
  Interpreter builds complete scope tree during AST construction.

- Interpeter manages global memory space and function space stack

- Interpreter implements external AST visitor

- Forward references support


High-level overview:

                   |                 +------------------------------------+
                   |  source code    |      Symbol Table / Scope Tree     |
                   |                 |                                    |
                  \|/                |      +-----------------------+     |
    +--------------X---------------+ |      |      GlobalScope      |     |
    |                              | |      +----/-------------\----+     |
    |     Regexp-based lexer       | |          /               \         |
    |                              | |+--------/-----+   +-------\-------+|
    +--------------+---------------+ ||FunctionSymbol|   |FunctionSymbol ||
                   |                 |+------X-------+   +-------X-------+|
                   |  token stream   |      /|\                 /|\       |
                  \|/                |       |                   |        |
    +--------------X---------------+ |+------+-------+   +-------+-------+|
    |                              | ||  LocalScope  |   |  LocalScope   ||
    |LL(k) recursive-descent parser| |+--------------+   +---------------+|
    |                              | +------------------------------------+
    +--------------+---------------+
                   |                 +------------------------------------+
                   |  AST            |           Memory Space             |
                  \|/                |                                    |
    +--------------X-------------+   |Function Space    Global Memory     |
    |        Interpreter         |   |Stack             Space             |
    | with external tree visitor |   |+-------------+   +----------------+|
    |                            |   ||FunctionSpace|   |  MemorySpace   ||
    +--------------+-------------+   |+-------------+   +----------------+|
                   |                 |+-------------+                     |
                   |  output         ||FunctionSpace|                     |
                  \|/                |+-------------+                     |
                   X                 +------------------------------------+



This Tree-Based Interpreter is similar to [Syntax-Directed Interpreter](http://github.com/rspivak/nososql) but instead of directly executing
source code during parsing the interpreter executes the source code by
constructing AST and then walking the tree.

Advantages of tree-based interperter over syntax-directed one:

1. Symbol definition and symbol resolution happen at different stages:
   - symbol definition is performed during parsing
   - symbol resolution is performed during interpretation

   This allows forward references and simplifies implementation -
   parser deals with scope tree only and interpreter deals with memory
   spaces.

2. More flexible because of AST as an intermediate representation.


Language grammar
----------------

    program             -> (function_definition | statement)+ EOF
    function_definition -> 'def' ID '(' (ID (',' ID)*)? ')' slist
    slist               -> ':' NL statement+ '.' NL
                           | statement
    statement           -> 'print' expr NL
                           | 'return' expr NL
                           | call NL
                           | assign NL
                           | 'if' expr slist ('else' slist)?
                           | 'while' expr slist
                           | NL
    assign              -> ID '=' expr
    expr                -> add_expr (('<' | '==') add_expr)?
    add_expr            -> mult_expr (('+' | '-') mult_expr)*
    mult_expr           -> atom ('*' atom)*
    atom                -> ID | INT | STRING | call | '(' expr ')'
    call                -> ID '(' (expr (',' expr)*)? ')'


Short language reference
------------------------

- statements: `print`, `return`, `if`, `while`,  and function call
- literals: integers and strings
- operators: <, ==, +, -, *

Expressions may contain identifiers.

Code examples
-------------

1. Factorial

        print factorial(6)               # forward reference

        def factorial(x):                # function definition
            if x < 2 return 1            # if statement
            return x * factorial(x - 1)  # return statement
        .                                # DOT marks the block end

2. WHILE loop

        index = 0

        while index < 10:
            print index
            index = index + 1
        .                                # DOT marks the block end

3. IF ELSE

        x = 10
        if x == 10 print 'Yes'
        else print 'No'

4. Variable lookup in different scopes

        x = 1        # global variable
        def foo(x):  # 'foo' is defined in global memory space
            print x  # prints 3 (parameter value)
        .            # DOT marks the block end
        def bar():   # 'bar' is defined in global memory space
            x = 7    # modify global variable
        .            # DOT marks the block end

        foo(3)       # prints 3
        bar()
        print x      # prints 7 ('bar' modified global variable)


AST Examples
------------

Trees in these examples are represented as S-expressions for tersness.

Function call:

    foo(5, 7)

    (CALL ID INT INT) means CALL is the root with children ID(foo), INT(5), and INT(7)

Function definition:

    def foo(x, y):
        z = x + y
        return z
    .

    (FUNC_DEF ID ID ID (BLOCK (ASSIGN ID (SUB ID ID)) (RETURN ID)))


Development
-----------

Install 'enscript' utility (optional).
If you are on Ubuntu:

    $ sudo apt-get install enscript

Boostrap the buildout and run it:

    $ cd tinypie
    $ python bootstrap.py
    $ bin/buildout

Run tests, test coverage and produce coverage reports:

    $ bin/test
    $ bin/coverage-test
    $ bin/coveragereport

    Check ./var/report/tinypie.html out for coverage report.

Run pep8 and pylint to check code style and search for potential bugs:

    $ bin/pep8
    $ bin/pylint

AST visualizer
--------------

To see how TinyPie AST for different language constructs looks
like you can use `gendot` command line utility that is generated
by buildout. This utility generates DOT file than can be further
processed by [dot](http://www.graphviz.org/) program to draw nice graphs.

    $ echo -n 'foo(3)' | bin/gendot
    digraph astgraph {
       node [shape=plaintext, fontsize=12, fontname="Courier", height=.1];
       ranksep=.3;
       edge [arrowsize=.5]

       node1 [label="BLOCK"];
       node2 [label="CALL"];
       node3 [label="ID (foo)"];
       node4 [label="INT (3)"];

       node2 -> node3
       node2 -> node4
       node1 -> node2
    }

    To draw graph and save it as a PNG image:

    $ echo -n 'foo(3)' | bin/gendot > funcall.dot
    $ dot -Tpng -o funcall.png funcall.dot


Bytecode Assembler
------------------

Converts assembly program into binary bytecodes.
The bytecode is further interpreted by the TinyPie
Register-Based Bytecode Interpreter / Virtual Machine.

TinyPie Assembly language grammar:

    program -> globals? (label | function_definition | instruction | NL)+
    globals -> '.globals' INT NL
    label -> ID ':' NL
    function_definition -> '.def' ID ':' 'args' '=' INT ',' 'locals' '=' INT NL
    instruction -> ID NL
                 | ID operand NL
                 | ID operand ',' operand NL
                 | ID operand ',' operand NL ',' operand NL
                 | 'call' operand
    operand -> REG | ID | STRING | INT


Assembler yields the following components:

1. *Code memory*: This is a `bytearray` containing
   bytecode instructions and their operands derived from
   the assembly source code.

2. *Global data memory size*: The number of slots allocated
   in global memory for use with GSTORE and GLOAD assembly commands.

3. *Program entry point*: An address of main function `.def main: ...`

4. *Constant pool*: A list of objects (integers, strings, function symbols)
   that are not part of the code memory. Bytecode instructions refer
   to those objects via integer index.


Here is a factorial function in TinyPie language:

    def factorial(x):
        if x < 2 return 1
        return x * factorial(x - 1)
    .

    print factorial(5)


Here is an equivalent TinyPie assembly code:

    .def factorial: args=1, locals=3
        # r1 holds argument 'n'
        loadk r2, 2
        lt r3, r1, r2        # n < 2 ?
        brf r3, cont         # if n >= 2 jump to 'cont'
        loadk r0, 1          # else return 1
        ret
    cont:
        loadk r2, 1          # r2 = 1
        move r3, r1          # r3 = n
        sub r1, r1, r2       # r1 = n - 1
        call factorial, r1   # factorial(n - 1)
        mul r0, r3, r0       # n = n * result of factorial(n - 1)
        ret

    .def main: args=0, locals=1
        loadk r1, 5
        call factorial, r1   # factorial(5)
        print r0             # 120
        halt

Here are the resulting elements produced by the Bytecode Assembler
by translating the above code assembly code:

    Constant pool:
    0000: <FunctionSymbol: name='factorial', address=0, args=1, locals=3>
    0001: 2
    0002: 1
    0003: <FunctionSymbol: name='main', address=95, args=0, locals=1>
    0004: 3

    Code memory:
    0000:   6   0   0   0   2   0   0   0
    0008:   1   4   0   0   0   3   0   0
    0016:   0   1   0   0   0   2  13   0
    0024:   0   0   3   0   0   0  41   6
    0032:   0   0   0   0   0   0   0   2
    0040:   9   6   0   0   0   2   0   0
    0048:   0   2  14   0   0   0   3   0
    0056:   0   0   1   2   0   0   0   1
    0064:   0   0   0   1   0   0   0   2
    0072:  16   0   0   0   0   0   0   0
    0080:   1   3   0   0   0   0   0   0
    0088:   0   3   0   0   0   0   9   6
    0096:   0   0   0   1   0   0   0   4
    0104:  16   0   0   0   0   0   0   0
    0112:   1  15   0   0   0   0  10

Bytecodes are described in the following section.


Register-Based Bytecode Interpreter / Virtual Machine
-----------------------------------------------------

                                       |
                               TinyPie | assembly
                                       |
                                      \|/
                            +----------X------------+
                            |                       |
                            |  Bytecode Assembler   |
                            |                       |
                            +----------+------------+
                                       |
                code memory(bytecode)  |  constant pool
                                      \|/
    +----------------------------------x---------------------------------------+
    |                                                                          |
    |          Register-Based Bytecode Interpreter / Virtual Machine           |
    |                                                                          |
    | +------------------------+        +------------------------------------+ |
    | |                        |        |       Function Call Stack          | |
    | |     Constant Pool      +----+   |                                    | |
    | |   (integer, string,    |    |   |                                    | |
    | |    function symbol)    |    |   | +--------------------------------+ | |
    | +------------------------+    |   | |        Stack Frame             | | |
    |                               |   | |                                | | |
    |                               |   | |function symbol: FS('main')     | | |
    |                               |   | |return address:  0              | | |
    | +------------------------+    |   | |          ret| args|locals      | | |
    | |                        |    |   | |registers: r0|r1 r2|r3 r4 r5    | | |
    | |  Global data memory    |    |   | +--------------------------------+ | |
    | |                        +-|  |   |                                    | |
    | |                        | |  |   |                                    | |
    | +------------------------+ |  |   | +--------------------------------+ | |
    |                            |  |   | |        Stack Frame             | | |
    |                            |  |   | |                                | | |
    |                            |  |   | |function symbol: FS('fact')     | | |
    | +------------------------+ |  |   | |return address: 17              | | |
    | |                        | |  |   | |          ret| args   |locals   | | |
    | |    Code memory         | |  |   | |registers: r0|r1 r2 r3|r4       | | |
    | |    (bytecode)          | |  |   | +--------------------------------+ | |
    | |                        | |  |   |                                    | |
    | +----------+-------------+ |  |   |                                    | |
    |            |               |  |   +------------------------------------+ |
    |           \|/              |  |                                          |
    + +----------X-------------+ |  |                                          |
    | |                        |/|  |                                          |
    | |         CPU            X-+  |                                          |
    | | (fetch-decode-execute) |\   |                                          |
    | |                        |/   |                                          |
    | +------------------------X----+                                          |
    |                           \                                              |
    +--------------------------------------------------------------------------+
