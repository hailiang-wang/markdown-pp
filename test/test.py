#!/usr/bin/env python
# -*- coding: utf-8 -*-
# ===============================================================================
#
# Copyright (c) 2020 <> All Rights Reserved
#
# Unit testing for MarkdownPP.
# File: /c/Users/Administrator/git/markup-markdown/tests/test.py
# Author: Hai Liang Wang
# Date: 2022-04-19:07:09:33
#
# ===============================================================================

"""

"""
from __future__ import absolute_import
from __future__ import print_function
from __future__ import unicode_literals

__copyright__ = "Copyright (c) 2020 . All Rights Reserved"
__author__ = "Hai Liang Wang"
__date__ = "2022-04-19:07:09:33"

import os
import sys
curdir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(curdir, os.pardir))

if sys.version_info[0] < 3:
    raise RuntimeError("Must be using Python 3")
else:
    unicode = str


import unittest
import os
import re
import subprocess
from markup import MarkdownPP
from markup import modules as Modules
from tempfile import NamedTemporaryFile

try:
    from StringIO import StringIO
except ImportError:
    from io import StringIO


class MarkdownPPTests(unittest.TestCase):

    def test_include(self):
        input = StringIO('foobar\n!INCLUDE "datafiles/test_include.md"\n')
        result = 'foobar\nThis is a test.\n'

        output = StringIO()
        MarkdownPP(input=input, modules=['include'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_glob(self):
        input = StringIO('foobar\n!INCLUDE "datafiles/test_glob_*.m.md"\n')
        expected_result = """foobar
This is a test.
Title
=====

Subtitle
--------

# Title
## Subtitle
### Subsubtitle
"""

        output = StringIO()
        MarkdownPP(input=input, modules=['include'], output=output)

        output.seek(0)
        actural_result = output.read()
        print(actural_result)

        # with open("t.txt", "w") as o:
        #     o.write(actural_result)

        self.assertEqual(actural_result, expected_result)

    def test_empty_glob_should_not_lead_to_index_errors(self):
        input = StringIO('!INCLUDE "datafiles/test_empty_glob.m.md"\n')
        result = '# Test Header\n'
        output = StringIO()
        MarkdownPP(input=input, modules=['include'], output=output)
        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_glob_recursive_relative_path(self):
        """Tests if the include works with recursive files and relative
        include path and globbing.
        """
        input = StringIO('yay\n!INCLUDE "datafiles/test_include_recursive.m.md"')
        result = """yay
# Parent
# File 1 Header

File 1 text
## File 2 Test

File 2 Text
File 00.md
File 01.md
"""
        output = StringIO()
        MarkdownPP(input=input, modules=['include'], output=output)
        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_url(self):
        input = StringIO('foobar\n!INCLUDEURL '
                         '"file:datafiles/test_include.md"\n')
        result = 'foobar\nThis is a test.\n'

        output = StringIO()
        MarkdownPP(input=input, modules=['includeurl'], output=output)

        output.seek(0)
        self.assertEqual(output.read().strip(), result.strip())

    def test_youtube(self):
        input = StringIO('foobar\n!VIDEO '
                         '"http://www.youtube.com/embed/7aEYoP5-duY"\n')
        result = ('foobar\n'
                  '[![Link to Youtube video](images/youtube/7aEYoP5-duY.png)]'
                  '(http://www.youtube.com/watch?v=7aEYoP5-duY)\n')

        output = StringIO()
        MarkdownPP(input=input, modules=['youtubeembed'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_toc(self):
        input = StringIO('\n# Document Title\n\n'
                         '!TOC\n\n'
                         '## Header 1\n'
                         '### Header 1.a\n'
                         '## Header 2\n')

        result = """
        # Document Title

        1\.  [Header 1](#header1)
        1.1\.  [Header 1.a](#header1.a)
        2\.  [Header 2](#header2)

        <a name="header1"></a>

        ## 1\. Header 1
        <a name="header1.a"></a>

        ### 1.1\. Header 1.a
        <a name="header2"></a>

        ## 2\. Header 2"""

        output = StringIO()
        MarkdownPP(input=input, modules=['tableofcontents'], output=output)

        output.seek(0)
        self.assertEqual([l.strip() for l in output.readlines()],
                         [l.strip() for l in result.split('\n')])

    def test_toc_with_code_block(self):
        input = StringIO(
            '!TOC\n'
            '# Header 1\n'
            '```\n'
            'code block\n'
            '``` \n'
            '# Header 2\n')

        result = """1\.  [Header 1](#header1)
        2\.  [Header 2](#header2)
        <a name="header1"></a>

        # 1\. Header 1
        ```
        code block
        ```
        <a name="header2"></a>
        
        # 2\. Header 2"""

        output = StringIO()
        MarkdownPP(input=input, modules=['tableofcontents'], output=output)
        output.seek(0)
        self.assertEqual([l.strip() for l in output.readlines()],
                         [l.strip() for l in result.split('\n')])

    def test_reference(self):
        input = StringIO('\n!REF\n\n[github]: http://github.com "GitHub"')
        result = ('\n*\t[GitHub][github]\n\n[github]: '
                  'http://github.com "GitHub"')

        output = StringIO()
        MarkdownPP(input=input, modules=['reference'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    @unittest.expectedFailure
    def test_latexrender(self):
        input = StringIO(r'$\displaystyle 1 + 1 = 2 $')
        result_re = (r'!\[\\displaystyle 1 \+ 1 = 2 \]'
                     r'\(http:\/\/quicklatex\.com\/.*\.png "'
                     r'\\displaystyle 1 \+ 1 = 2 "\)')

        output = StringIO()
        MarkdownPP(input=input, modules=['latexrender'], output=output)

        output.seek(0)
        output_str = output.read().strip()
        match = re.match(result_re, output_str)
        self.assertIsNotNone(match)
        self.assertEqual(match.span(), (0, len(output_str)))

    def test_file(self):
        with open('../readme.md', 'r') as md:
            result = md.read()

        with open('../readme.m.md', 'r') as mdpp:
            input = mdpp

            output = StringIO()
            modules = list(Modules.keys())
            MarkdownPP(input=input, modules=modules, output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_shift(self):
        # test shift=1
        input = StringIO('!INCLUDE "datafiles/test_shift.m.md", 1\n')
        with open('datafiles/test_shift.md', 'r') as resfile:
            result = resfile.read()

        output = StringIO()
        MarkdownPP(input=input, modules=['include'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

        # test shift=2, by shifting again the previous output
        output.seek(0)
        with NamedTemporaryFile(delete=False) as temp:
            temp.write(output.read().encode('utf-8'))
            name = temp.name

        input1 = StringIO('!INCLUDE "{}", 1\n'.format(name))
        output1 = StringIO()
        MarkdownPP(input=input1, modules=['include'], output=output1)

        input2 = StringIO('!INCLUDE "datafiles/test_shift.m.md", 2\n')
        output2 = StringIO()
        MarkdownPP(input=input2, modules=['include'], output=output2)

        output1.seek(0)
        output2.seek(0)

        self.assertEqual(output1.read(), output2.read())
        os.remove(name)

    def test_script(self):
        # test the script without arguments
        with NamedTemporaryFile(delete=False) as temp_outfile:
            # source_file = os.path.join(curdir, 'datafiles', 'test_script.m.md')
            source_file = os.path.join('datafiles', 'test_script.m.md')
            print("source_file", source_file)
            subprocess.call(['markup', source_file, '-o',
                             temp_outfile.name], shell=True, cwd=curdir)

            tmp_file = os.path.join(curdir, os.pardir, "tmp", "test_script.txt")
            with open(tmp_file, "w") as out:
                temp_outfile.seek(0)
                out.write(temp_outfile.read().decode('utf-8'))

            with open(os.path.join(curdir, 'datafiles', 'test_script.txt'), 'r') as target_outfile, open(tmp_file, "r") as generated:
                self.assertEqual(target_outfile.read(), generated.read())

    def test_include_code(self):
        input = StringIO('foo\n!INCLUDECODE "datafiles/test_include_code.py"\nbar')
        result = """foo
```
def main():
    print "Hello World"


if __name__ == '__main__':
    main()

```
bar"""
        output = StringIO()
        MarkdownPP(input=input, modules=['includecode'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_toc_table_figure(self):
        # test the script without arguments
        with NamedTemporaryFile(delete=False) as temp_outfile:
            # source_file = os.path.join(curdir, 'datafiles', 'test_script.m.md')
            source_file = os.path.join('datafiles', 'test_toc_table_figure.m.md')
            # print("source_file", source_file)
            subprocess.call(['markup', source_file, '-o',
                             temp_outfile.name], shell=True, cwd=curdir)

            tmp_file = os.path.join(curdir, os.pardir, "tmp", "test_toc_table_figure.md")
            with open(tmp_file, "w", encoding="UTF-8") as out:
                temp_outfile.seek(0)
                out.write(temp_outfile.read().decode('utf-8'))

            self.assertTrue(True)

            # with open(os.path.join(curdir, 'datafiles', 'test_script.txt'), 'r') as target_outfile, open(tmp_file, "r") as generated:
            #     self.assertEqual(target_outfile.read(), generated.read())

    def test_include_code_lines(self):
        input = StringIO('foo\n!INCLUDECODE "datafiles/test_include_code_2.py" (python), 1:10\nbar')
        result = """foo
```python
def main():
    print "Hello World"






if __name__ == '__main__':
    main()

```
bar"""
        output = StringIO()
        MarkdownPP(input=input, modules=['includecode'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_code_single_line(self):
        input = StringIO('foo\n!INCLUDECODE "datafiles/test_include_code.py",1\nbar')
        result = """foo
```
def main():

```
bar"""
        output = StringIO()
        MarkdownPP(input=input, modules=['includecode'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_code_multiline_1(self):
        input = StringIO('foo\n!INCLUDECODE "datafiles/test_include_code.py",5:\nbar')
        result = """foo
```
if __name__ == '__main__':
    main()

```
bar"""
        output = StringIO()
        MarkdownPP(input=input, modules=['includecode'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_code_multiline_2(self):
        input = StringIO('foo\n!INCLUDECODE "datafiles/test_include_code.py",5:5\nbar')
        result = """foo
```
if __name__ == '__main__':

```
bar"""
        output = StringIO()
        MarkdownPP(input=input, modules=['includecode'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_code_multiline_3(self):
        input = StringIO('foo\n!INCLUDECODE "datafiles/test_include_code.py",:3\nbar')
        result = """foo
```
def main():
    print "Hello World"


```
bar"""
        output = StringIO()
        MarkdownPP(input=input, modules=['includecode'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_code_lang(self):
        input = StringIO('foo\n!INCLUDECODE "datafiles/test_include_code.py"(python)\nbar')
        result = """foo
```python
def main():
    print "Hello World"


if __name__ == '__main__':
    main()

```
bar"""
        output = StringIO()
        MarkdownPP(input=input, modules=['includecode'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)

    def test_include_code_lang_with_multiline(self):
        input = StringIO('foo\n!INCLUDECODE "datafiles/test_include_code.py"(python),1:3\nbar')
        result = """foo
```python
def main():
    print "Hello World"


```
bar"""
        output = StringIO()
        MarkdownPP(input=input, modules=['includecode'], output=output)

        output.seek(0)
        self.assertEqual(output.read(), result)


if __name__ == '__main__':
    unittest.main()
