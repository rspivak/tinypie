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

        (or run alternatively easy_install: `$ sudo easy_install tinypie`)

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
        .

2. WHILE loop

        index = 0

        while index < 10:
            print index
            index = index + 1
        .

3. IF ELSE

        x = 10
        if x == 10 print 'Yes'
        else print 'No'

3. Variable lookup in different scopes

        x = 1        # global variable
        def foo(x):  # 'foo' is defined in global memory space
            print x  # prints 3 (parameter value)
        .
        def bar():   # 'bar' is defined in global memory space
            x = 7    # modify global variable
        .

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
