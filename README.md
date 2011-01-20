TinyPie - Tree-Based Interpreter for TinyPie language
=====================================================

Overview
--------

TinyPie is a tree-based interpreter for a simple programming
language with a Python-like syntax.

It's based on Pie language from [Language Implementation Patterns]
(http://pragprog.com/titles/tpdsl/language-implementation-patterns) Ch.9

Quote from the book: "A tree-based interpreter is like a compiler front
end with an interpreter grafted onto the end instead of a code generator"


Goals of the project
-------------------

1. Self-education

2. To serve as an example for people interested in crafting
   their own interpreter in Python for a simple programming language or DSL


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



This Tree-Based Interpreter is similar to [Syntax-Directed Interpreter]
(http://github.com/rspivak/nososql) but instead of directly executing
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
















