#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, 51 Franklin Street, Fifth Floor, Boston, MA 02110-1335, USA.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#

import codecs
import os.path
import re
import sys
import pkg_resources
import unittest

from setuptools import setup, Command

here = os.path.abspath(os.path.dirname(__file__))
readme_md = os.path.join(here, 'README.md')
version_py = os.path.join(here, 'graal', '_version.py')

# Pypi wants the description to be in reStrcuturedText, but
# we have it in Markdown. So, let's convert formats.
# Set up thinkgs so that if pypandoc is not installed, it
# just issues a warning.
try:
    import pypandoc
    long_description = pypandoc.convert(readme_md, 'rst')
except (IOError, ImportError):
    print("Warning: pypandoc module not found, or pandoc not installed. " + "Using md instead of rst")
    with codecs.open(readme_md, encoding='utf-8') as f:
        long_description = f.read()


with codecs.open(version_py, 'r', encoding='utf-8') as fd:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]',
                        fd.read(), re.MULTILINE).group(1)


class TestCommand(Command):

    user_options = []
    __dir__ = os.path.dirname(os.path.realpath(__file__))

    def initialize_options(self):
        os.chdir(os.path.join(self.__dir__, 'tests'))

    def finalize_options(self):
        pass

    def run(self):
        # To ensure it gets Perceval from the right directory, set first position of sys.path
        sys.path.insert(0, pkg_resources.get_distribution("perceval").location)
        test_suite = unittest.TestLoader().discover('.', pattern='test*.py')
        result = unittest.TextTestRunner(buffer=True).run(test_suite)
        sys.exit(not result.wasSuccessful())


cmdclass = {'test': TestCommand}

setup(name="graal",
      description="A generic source code analyzer",
      long_description="Graal extends the Git backend of Perceval to enable source code analysis. Thus, "
                       "it fetches the commits from a Git repository and provides a mechanism to plug third party "
                       "tools/libraries focused on source code analysis",
      url="https://github.com/chaoss/grimoirelab-graal",
      version=version,
      author="Bitergia",
      author_email="valcos@bitergia.com",
      license="GPLv3",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
          'Programming Language :: Python :: 3'
      ],
      keywords="git source code analysis loc cyclomatic complexity",
      packages=[
          'graal',
          'graal.backends',
          'graal.backends.core',
          'graal.backends.core.analyzers'
      ],
      namespace_packages=['graal', 'graal.backends'],
      install_requires=[
          'lizard>=1.14.10',
          'perceval>=0.12.0',
          'pylint>=1.8.4',
          'networkx>=2.1',
          'pydot>=1.2.4',
          'bandit>=1.4.0'
      ],
      scripts=[
          'bin/graal'
      ],
      cmdclass=cmdclass,
      zip_safe=False)
