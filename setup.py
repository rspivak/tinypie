import os

from setuptools import setup, find_packages

classifiers = """\
Intended Audience :: Developers
License :: OSI Approved :: MIT License
Programming Language :: Python
Topic :: Software Development :: Interpreters
Operating System :: Unix
"""

def read(*rel_names):
    return open(os.path.join(os.path.dirname(__file__), *rel_names)).read()

setup(
    name='tinypie',
    version='0.2',
    url='http://github.com/rspivak/tinypie',
    license='MIT',
    description='Tree-Based Interpreter, Compiler and VM for TinyPie language',
    author='Ruslan Spivak',
    author_email='ruslan.spivak@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    install_requires=['setuptools'],
    zip_safe=False,
    entry_points="""\
    [console_scripts]
    tinypie = tinypie.interpreter:main
    tpvm = tinypie.vm:main
    gendot = tinypie.astviz:generate_dot
    """,
    classifiers=filter(None, classifiers.split('\n')),
    long_description=read('README.md') + '\n\n' + read('CHANGES.txt'),
    include_package_data=True,
    extras_require={'test': ['Jinja2']}
    )
