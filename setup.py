from setuptools import setup, find_packages

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Interpreters
Operating System :: Unix
"""

long_description = """\
Overview
---------

This is an example of a Tree-Based Interpreter
for a simple TinyPie language
"""

setup(
    name='tinypie',
    version='0.1',
    url='http://github.com/rspivak/tinypie',
    license='MIT',
    description='Tree-Based Interpreter for a simple TinyPie language',
    author='Ruslan Spivak',
    author_email='ruslan.spivak@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    tinypie = tinypie.interpreter:main
    """,
    classifiers=filter(None, classifiers.split('\n')),
    long_description=long_description
    )
