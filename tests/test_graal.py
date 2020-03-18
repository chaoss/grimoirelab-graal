#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015-2020 Bitergia
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
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
# Authors:
#     Valerio Cosentino <valcos@bitergia.com>
#     inishchith <inishchith@gmail.com>
#

import io
import os
import shutil
import tarfile
import tempfile
import unittest
import unittest.mock

from grimoirelab_toolkit.datetime import str_to_datetime
from perceval.errors import RepositoryError
from perceval.utils import DEFAULT_DATETIME, DEFAULT_LAST_DATETIME

import graal
from graal.graal import (DEFAULT_WORKTREE_PATH,
                         CATEGORY_GRAAL,
                         GIT_EXEC_PATH,
                         Graal,
                         GraalCommand,
                         GraalRepository,
                         GraalCommandArgumentParser,
                         logger)
from base_repo import TestCaseRepo


CATEGORY_MOCKED = 'mocked'


class MockedGraalRepository(GraalRepository):

    RAISE_EXCEPTION = False

    def __init__(self, uri, dirpath, raise_exception):
        super().__init__(uri, dirpath)
        self.worktreepath = None
        MockedGraalRepository.RAISE_EXCEPTION = raise_exception

    @staticmethod
    def _exec(cmd, cwd=None, env=None, ignored_error_codes=None,
              encoding='utf-8'):

        if MockedGraalRepository.RAISE_EXCEPTION:
            if cmd[:2] == [GIT_EXEC_PATH, "archive"]:
                raise OSError

            raise RepositoryError(cause='oops!')

        super()._exec(cmd, cwd=cwd, env=env, ignored_error_codes=ignored_error_codes,
                      encoding=encoding)


class MockedGraal(Graal):

    CATEGORIES = [CATEGORY_MOCKED]

    def __init__(self, uri, gitpath, worktreepath=DEFAULT_WORKTREE_PATH,
                 entrypoint=None, in_paths=None, out_paths=None, details=False,
                 tag=None, archive=None, raise_exception=False):
        super().__init__(uri, gitpath, worktreepath=worktreepath, entrypoint=entrypoint,
                         in_paths=in_paths, out_paths=out_paths, details=details,
                         tag=tag, archive=archive)
        self.raise_exception = raise_exception

    def fetch(self, category=CATEGORY_MOCKED, paths=None,
              from_date=DEFAULT_DATETIME, to_date=DEFAULT_LAST_DATETIME,
              branches=None, latest_items=False):
        """Fetch commits and add code complexity information."""

        items = super().fetch(category,
                              from_date=from_date, to_date=to_date,
                              branches=branches, latest_items=latest_items)

        return items

    @staticmethod
    def metadata_category(item):
        """Extracts the category from a MockedGraal item.

        This backend only generates one type of item which is
        'mocked'.
        """
        return CATEGORY_MOCKED

    def _filter_commit(self, commit):
        """Filter a commit according to its data (e.g., author, sha, etc.)

        :param commit: a Perceval commit item

        :returns: a boolean value
        """
        return False

    def _analyze(self, commit, paths=None):
        """Analyse a commit and the corresponding
        checkout version of the repository

        :param commit: a Perceval commit item
        :param paths: a list of paths to narrow the analysis
        """
        mods = 0
        for f in commit['files']:
            added = int(f['added']) if 'added' in f else 0
            removed = int(f['removed']) if 'removed' in f else 0
            mods += (added - removed)

        return {'lines_modified': mods}

    def _post(self, commit):
        """Perform operation (e.g., removing attributes) on the Graal item obtained

        :param commit: a Graal commit item
        """
        if self.raise_exception:
            raise Exception

        commit.pop('Author', None)
        commit.pop('Commit', None)
        commit.pop('files', None)
        commit.pop('parents', None)
        commit.pop('refs', None)
        return commit


class MockedGraalCommand(GraalCommand):
    BACKEND = MockedGraal

    @classmethod
    def setup_cmd_parser(cls):

        parser = GraalCommand.setup_cmd_parser(cls.BACKEND)

        return parser


class CommandBackend(MockedGraal):
    """Backend used for testing in BackendCommand tests"""

    def fetch_items(self, category, **kwargs):
        for item in super().fetch_items(category, **kwargs):
            yield item


class ErrorCommandBackend(CommandBackend):
    """Backend which raises an exception while fetching items"""

    def fetch_items(self, category, **kwargs):
        for item in super().fetch_items(category, **kwargs):
            yield item
            raise Exception


class TestGraalBackend(TestCaseRepo):
    """Graal backend tests"""

    def test_initialization(self):
        """Test whether attributes are initializated"""

        graal = Graal('http://example.com', self.git_path, self.worktree_path, tag='test')
        self.assertEqual(graal.uri, 'http://example.com')
        self.assertEqual(graal.gitpath, self.git_path)
        self.assertEqual(graal.worktreepath, os.path.join(self.worktree_path, os.path.split(graal.gitpath)[1]))
        self.assertEqual(graal.origin, 'http://example.com')
        self.assertEqual(graal.tag, 'test')
        self.assertIsNone(graal.entrypoint)
        self.assertIsNone(graal.in_paths)
        self.assertIsNone(graal.out_paths)
        self.assertFalse(graal.details)
        self.assertIsNone(graal.exec_path)

        # When tag is empty or None it will be set to the value in uri
        graal = Graal('http://example.com', self.git_path, self.worktree_path)
        self.assertEqual(graal.origin, 'http://example.com')
        self.assertEqual(graal.tag, 'http://example.com')
        self.assertIsNone(graal.exec_path)

        graal = Graal('http://example.com', self.git_path, self.worktree_path)
        self.assertEqual(graal.origin, 'http://example.com')
        self.assertEqual(graal.tag, 'http://example.com')
        self.assertIsNone(graal.exec_path)

        graal = Graal('http://example.com', self.git_path, self.worktree_path, exec_path='/tmp/nomossa')
        self.assertEqual(graal.origin, 'http://example.com')
        self.assertEqual(graal.tag, 'http://example.com')
        self.assertEqual(graal.exec_path, '/tmp/nomossa')

        graal = Graal('http://example.com', self.git_path,
                      entrypoint="entrypoint", in_paths=["x"], out_paths=["y"], details=True)
        self.assertEqual(graal.worktreepath, os.path.join(DEFAULT_WORKTREE_PATH, os.path.split(graal.gitpath)[1]))
        self.assertEqual(graal.entrypoint, "entrypoint")
        self.assertEqual(graal.in_paths, ["x"])
        self.assertEqual(graal.out_paths, ["y"])
        self.assertTrue(graal.details)
        self.assertIsNone(graal.exec_path)

    def test_fetch_no_analysis(self):
        """Test whether commits are inflated with the analysis attribute"""

        graal = Graal('http://example.com', self.git_path, self.worktree_path)
        commits = [commit for commit in graal.fetch()]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(graal.worktreepath))

        for commit in commits:
            self.assertEqual(commit['backend_name'], 'Graal')
            self.assertEqual(commit['category'], CATEGORY_GRAAL)
            self.assertEqual(commit['data']['analysis'], {})

    def test_fetch_analysis(self):
        """Test whether commits are properly processed"""

        mocked = MockedGraal('http://example.com', self.git_path, self.worktree_path)
        commits = [commit for commit in mocked.fetch()]

        self.assertEqual(len(commits), 6)
        self.assertFalse(os.path.exists(mocked.worktreepath))

        commit = commits[0]
        self.assertEqual(commit['backend_name'], 'MockedGraal')
        self.assertEqual(commit['category'], CATEGORY_MOCKED)
        self.assertEqual(commit['data']['analysis']['lines_modified'], 4177)
        self.assertFalse('Author' in commit['data'])
        self.assertFalse('Commit' in commit['data'])
        self.assertFalse('files' in commit['data'])
        self.assertFalse('parents' in commit['data'])
        self.assertFalse('refs' in commit['data'])

        commit = commits[1]
        self.assertEqual(commit['backend_name'], 'MockedGraal')
        self.assertEqual(commit['category'], CATEGORY_MOCKED)
        self.assertEqual(commit['data']['analysis']['lines_modified'], 25)
        self.assertFalse('Author' in commit['data'])
        self.assertFalse('Commit' in commit['data'])
        self.assertFalse('files' in commit['data'])
        self.assertFalse('parents' in commit['data'])
        self.assertFalse('refs' in commit['data'])

        commit = commits[2]
        self.assertEqual(commit['backend_name'], 'MockedGraal')
        self.assertEqual(commit['category'], CATEGORY_MOCKED)
        self.assertEqual(commit['data']['analysis']['lines_modified'], 12)
        self.assertFalse('Author' in commit['data'])
        self.assertFalse('Commit' in commit['data'])
        self.assertFalse('files' in commit['data'])
        self.assertFalse('parents' in commit['data'])
        self.assertFalse('refs' in commit['data'])

    def test_fetch_analysis_on_error(self):
        mocked = MockedGraal('http://example.com', self.git_path, self.worktree_path, raise_exception=True)
        with self.assertRaises(Exception):
            _ = [commit for commit in mocked.fetch()]


class TestGraalRepository(TestCaseRepo):
    """GraalRepository tests"""

    def setUp(self):
        super().setUp()

        patcher = unittest.mock.patch('os.getenv')
        self.addCleanup(patcher.stop)
        self.mock_getenv = patcher.start()
        self.mock_getenv.return_value = ''

    def tearDown(self):
        repo = GraalRepository('http://example.git', self.git_path)
        try:
            repo._exec(['git', 'branch', '-D', 'testworktree'], cwd=repo.dirpath, env=repo.gitenv)
            repo._exec(['git', 'branch', '-D', 'graaltest'], cwd=repo.dirpath, env=repo.gitenv)
        except RepositoryError:
            pass

    def test_init(self):
        """Test initialization"""

        repo = GraalRepository('http://example.git', self.git_path)

        self.assertIsInstance(repo, GraalRepository)
        self.assertEqual(repo.uri, 'http://example.git')
        self.assertEqual(repo.dirpath, self.git_path)

        # Check command environment variables
        expected = {
            'LANG': 'C',
            'PAGER': '',
            'HOME': '',
            'HTTPS_PROXY': '',
            'HTTP_PROXY': '',
            'NO_PROXY': ''
        }
        self.assertDictEqual(repo.gitenv, expected)

    def test_worktree(self):
        """Test whether a working tree is created"""

        new_path = os.path.join(self.tmp_path, 'testworktree')

        repo = GraalRepository('http://example.git', self.git_path)
        self.assertIsNone(repo.worktreepath)
        repo.worktree(new_path)
        self.assertEqual(repo.worktreepath, new_path)
        self.assertTrue(os.path.exists(repo.worktreepath))

        repo.prune()
        self.assertFalse(os.path.exists(repo.worktreepath))

    def test_worktree_from_branch(self):
        """Test whether a working tree is created from a target branch"""

        new_path = os.path.join(self.tmp_path, 'testworktree')

        repo = GraalRepository('http://example.git', self.git_path)

        self.assertIsNone(repo.worktreepath)
        repo.worktree(new_path, branch='master')
        self.assertEqual(repo.worktreepath, new_path)
        self.assertTrue(os.path.exists(repo.worktreepath))

        repo.prune()
        self.assertFalse(os.path.exists(repo.worktreepath))

    def test_worktree_already_exists(self):
        """Test whether a debug info is logged when the worktree already exists"""

        new_path = os.path.join(self.tmp_path, 'testworktree')

        repo = GraalRepository('http://example.git', self.git_path)
        self.assertIsNone(repo.worktreepath)
        repo.worktree(new_path, branch='master')

        with self.assertLogs(logger, level='DEBUG') as cm:
            repo.worktree(new_path, branch='master')
            self.assertRegex(cm.output[0], 'DEBUG:graal.graal:Git worktree.*not created.*already exists.*')

        repo.prune()
        self.assertFalse(os.path.exists(repo.worktreepath))

    def test_worktree_on_error(self):
        """Test whether a RepositoryError is thrown in case of error"""

        new_path = os.path.join(self.tmp_path, 'testworktree')

        repo = MockedGraalRepository('http://example.git', self.git_path, raise_exception=True)
        with self.assertRaises(RepositoryError):
            repo.worktree(new_path)

    def test_prune(self):
        """Test whether a working tree is deleted"""

        new_path = os.path.join(self.tmp_path, 'testworktree')

        repo = GraalRepository('http://example.git', self.git_path)
        repo.worktreepath = new_path
        repo.worktree(new_path)
        self.assertEqual(repo.worktreepath, new_path)
        self.assertTrue(os.path.exists(repo.worktreepath))

        repo.prune()
        self.assertFalse(os.path.exists(repo.worktreepath))

    def test_prune_on_error(self):
        """Test whether a RepositoryError is thrown in case of error"""

        repo = MockedGraalRepository('http://example.git', self.git_path, raise_exception=True)
        with self.assertRaises(RepositoryError):
            repo.prune()

    def test_checkout(self):
        """Test whether Git checkout commands are correctly executed"""

        new_path = os.path.join(self.tmp_path, 'testworktree')

        repo = GraalRepository('http://example.git', self.git_path)
        self.assertIsNone(repo.worktreepath)
        repo.worktree(new_path)

        repo.checkout("075f0c6161db5a3b1c8eca45e08b88469bb148b9")
        current_commit_hash = self.__git_show_hash(repo)
        self.assertEqual("075f0c6161db5a3b1c8eca45e08b88469bb148b9", current_commit_hash)

        repo.checkout("4f3b403d47fb291a9a942a62d62c24faa79244c8")
        current_commit_hash = self.__git_show_hash(repo)
        self.assertEqual("4f3b403d47fb291a9a942a62d62c24faa79244c8", current_commit_hash)

        repo.checkout("825b4da7ca740f7f2abbae1b3402908a44d130cd")
        current_commit_hash = self.__git_show_hash(repo)
        self.assertEqual("825b4da7ca740f7f2abbae1b3402908a44d130cd", current_commit_hash)

        repo.prune()
        self.assertFalse(os.path.exists(repo.worktreepath))

    def test_checkout_on_error(self):
        """Test whether a RepositoryError is thrown in case of error"""

        repo = MockedGraalRepository('http://example.git', self.git_path, raise_exception=True)
        with self.assertRaises(RepositoryError):
            repo.checkout("825b4da7ca740f7f2abbae1b3402908a44d130cd")

    def test_archive(self):
        """Test whether a Git archive command is correctly executed"""

        repo = GraalRepository('http://example.git', self.git_path)
        file_obj = repo.archive("825b4da7ca740f7f2abbae1b3402908a44d130cd")

        self.assertIsInstance(file_obj, io.BytesIO)

    def test_archive_on_error(self):
        """Test whether the method return nothing in case of error"""

        repo = MockedGraalRepository('http://example.git', self.git_path, raise_exception=True)
        file_obj = repo.archive("825b4da7ca740f7f2abbae1b3402908a44d130cd")
        self.assertIsNone(file_obj)

    def test_tar_obj(self):
        """Test whether a BytesIO object is converted to a tar object"""

        repo = GraalRepository('http://example.git', self.git_path)
        file_obj = repo.archive("825b4da7ca740f7f2abbae1b3402908a44d130cd")

        tar_obj = repo.tar_obj(file_obj)
        self.assertIsInstance(tar_obj, tarfile.TarFile)

    def test_tar_obj_on_error(self):
        """Test whether the method return nothing in case of error"""

        repo = GraalRepository('http://example.git', self.git_path)
        file_obj = io.BytesIO(b'abcdefghilmnopqrstuvz')
        tar_obj = repo.tar_obj(file_obj)
        self.assertIsNone(tar_obj)

    def test_filter_tar(self):
        """Test whether tar object members are filtered"""

        repo = GraalRepository('http://example.git', self.git_path)
        file_obj = repo.archive("825b4da7ca740f7f2abbae1b3402908a44d130cd")
        tar_obj = repo.tar_obj(file_obj)
        self.assertEqual(len(tar_obj.getmembers()), 18)

        to_select = ['.gitignore']
        filtered_obj = repo.filter_tar(tar_obj, to_select)
        self.assertEqual(len(filtered_obj.getmembers()), 1)
        self.assertEqual(filtered_obj.getmembers()[0].name, '.gitignore')

    def test_filter_tar_no_members(self):
        """Test whether an null object is returned if not members are present"""

        repo = GraalRepository('http://example.git', self.git_path)
        file_obj = repo.archive("825b4da7ca740f7f2abbae1b3402908a44d130cd")
        tar_obj = repo.tar_obj(file_obj)

        to_select = []
        filtered_obj = repo.filter_tar(tar_obj, to_select)
        self.assertIsNone(filtered_obj)

    def test_tar(self):
        """Test whether tar object is saved to disk"""

        tar_path = os.path.join(self.tmp_path, 'testtar.tar.gz')

        repo = GraalRepository('http://example.git', self.git_path)
        file_obj = repo.archive("825b4da7ca740f7f2abbae1b3402908a44d130cd")
        tar_obj = repo.tar_obj(file_obj)

        repo.tar(tar_obj, tar_path)

        self.assertTrue(os.path.exists(tar_path))
        self.assertTrue(os.path.isfile(tar_path))

        os.remove(tar_path)

    def test_exists(self):
        """Test whether the method exists works properly"""

        exists_path = os.path.join(self.tmp_path, 'existtest')

        self.assertFalse(GraalRepository.exists(exists_path))
        f = open(exists_path, 'w')
        f.close()
        self.assertTrue(GraalRepository.exists(exists_path))

    def test_untar(self):
        """Test whether tar file is untarred"""

        untar_path = os.path.join(self.tmp_path, 'untesttar')

        repo = GraalRepository('http://example.git', self.git_path)
        file_obj = repo.archive("825b4da7ca740f7f2abbae1b3402908a44d130cd")
        tar_obj = repo.tar_obj(file_obj)

        repo.untar(tar_obj, untar_path)
        self.assertTrue(os.path.exists(untar_path))
        self.assertTrue(os.path.isdir(untar_path))

        shutil.rmtree(untar_path)

    def test_extension(self):
        """Test whether file extensions are identified"""

        self.assertEqual(GraalRepository.extension('setup.py'), 'py')
        self.assertEqual(GraalRepository.extension('tests/requirements.txt'), 'txt')
        self.assertEqual(GraalRepository.extension('LICENSE'), 'LICENSE')

    def test_files(self):
        """Test whether all files in a directory and its sub-directories are shown"""

        new_path = os.path.join(self.tmp_path, 'testworktree')

        repo = GraalRepository('http://example.git', self.git_path)
        repo.worktree(new_path)

        expected = [os.path.join(new_path, 'perceval/archive.py'),
                    os.path.join(new_path, 'perceval/backend.py'),
                    os.path.join(new_path, 'perceval/client.py'),
                    os.path.join(new_path, 'perceval/__init__.py'),
                    os.path.join(new_path, 'perceval/_version.py'),
                    os.path.join(new_path, 'perceval/utils.py'),
                    os.path.join(new_path, 'perceval/errors.py'),
                    os.path.join(new_path, 'perceval/backends/__init__.py'),
                    os.path.join(new_path, 'perceval/backends/core/__init__.py'),
                    os.path.join(new_path, 'perceval/backends/core/github.py'),
                    os.path.join(new_path, 'perceval/backends/core/mbox.py'),
                    os.path.join(new_path, 'perceval/backends/core/git.py')
                    ]

        files = repo.files(new_path)

        self.assertEqual(len(files), len(expected))
        for f in files:
            self.assertIn(f, expected)

        repo.prune()
        self.assertFalse(os.path.exists(repo.worktreepath))

    def test_files_no_dir(self):
        """Test whether an empty list is returned when the input is none"""

        repo = GraalRepository('http://example.git', self.git_path)
        files = repo.files(None)
        self.assertEqual(files, [])

    def test_delete(self):
        """Test whether files and directories are deleted"""

        new_path = os.path.join(self.tmp_path, 'testworktree')

        repo = GraalRepository('http://example.git', self.git_path)
        repo.worktree(new_path)

        target_file = os.path.join(new_path, 'perceval/_version.py')
        target_folder = os.path.join(new_path, 'perceval/backends')

        self.assertTrue(os.path.exists(target_file))
        repo.delete(target_file)
        self.assertFalse(os.path.exists(target_file))

        self.assertTrue(os.path.exists(target_folder))
        repo.delete(target_folder)
        self.assertFalse(os.path.exists(target_folder))

        repo.prune()
        self.assertFalse(os.path.exists(repo.worktreepath))

    @staticmethod
    def __git_show_hash(repo):
        cmd_show = [GIT_EXEC_PATH, 'show']
        try:
            outs = repo._exec(cmd_show, cwd=repo.worktreepath, env=repo.gitenv)
        except Exception:
            return None

        outs = outs.decode("utf-8")
        hash = outs.split("\n")[0].replace("commit ", "")
        return hash


class TestGraalCommand(unittest.TestCase):
    """GraalCommand tests"""

    def setUp(self):
        super().setUp()
        self.tmp_path = tempfile.mkdtemp(prefix='graal_')

    def tearDown(self):
        super().tearDown()
        shutil.rmtree(self.tmp_path)

    def test_backend_class(self):
        """Test if the backend class is Graal"""

        self.assertIs(GraalCommand.BACKEND, Graal)

    @unittest.mock.patch('os.path.expanduser')
    def test_gitpath_init(self, mock_expanduser):
        """Test gitpath initialization"""

        mock_expanduser.return_value = os.path.join(self.tmp_path, 'testpath')
        args = ['http://example.com/']

        cmd = MockedGraalCommand(*args)
        self.assertEqual(cmd.parsed_args.git_path,
                         os.path.join(self.tmp_path, 'testpath/http://example.com/' + '-git'))

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath']

        cmd = MockedGraalCommand(*args)
        self.assertEqual(cmd.parsed_args.git_path, '/tmp/gitpath')

    def test_setup_cmd_parser(self):
        """Test if it parser object is correctly initialized"""

        parser = GraalCommand.setup_cmd_parser(Graal)
        self.assertIsInstance(parser, GraalCommandArgumentParser)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)
        self.assertEqual(parsed_args.to_date, None)
        self.assertEqual(parsed_args.branches, None)
        self.assertFalse(parsed_args.latest_items)
        self.assertEqual(parsed_args.worktreepath, DEFAULT_WORKTREE_PATH)
        self.assertEqual(parsed_args.in_paths, None)
        self.assertEqual(parsed_args.out_paths, None)
        self.assertEqual(parsed_args.entrypoint, None)
        self.assertFalse(parsed_args.details)
        self.assertEqual(parser._backend, Graal)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test',
                '--from-date', '1975-01-01',
                '--to-date', '2099-01-01',
                '--branches', 'master', 'testing',
                '--latest-items',
                '--worktree-path', '/tmp/custom-worktrees/',
                '--in-paths', '*.py', '*.java',
                '--out-paths', '*.c',
                '--entrypoint', 'module',
                '--details']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, str_to_datetime('1975-01-01'))
        self.assertEqual(parsed_args.to_date, str_to_datetime('2099-01-01'))
        self.assertEqual(parsed_args.branches, ['master', 'testing'])
        self.assertTrue(parsed_args.latest_items)
        self.assertEqual(parsed_args.worktreepath, '/tmp/custom-worktrees/')
        self.assertEqual(parsed_args.in_paths, ['*.py', '*.java'])
        self.assertEqual(parsed_args.out_paths, ['*.c'])
        self.assertEqual(parsed_args.entrypoint, 'module')
        self.assertTrue(parsed_args.details)

        parser = GraalCommand.setup_cmd_parser(Graal)
        self.assertIsInstance(parser, GraalCommandArgumentParser)

        args = ['http://example.com/',
                '--git-path', '/tmp/gitpath',
                '--tag', 'test',
                '--exec-path', '/tmp/execpath']

        parsed_args = parser.parse(*args)
        self.assertEqual(parsed_args.uri, 'http://example.com/')
        self.assertEqual(parsed_args.git_path, '/tmp/gitpath')
        self.assertEqual(parsed_args.exec_path, '/tmp/execpath')
        self.assertEqual(parsed_args.tag, 'test')
        self.assertEqual(parsed_args.from_date, DEFAULT_DATETIME)
        self.assertEqual(parsed_args.to_date, None)
        self.assertEqual(parsed_args.branches, None)
        self.assertFalse(parsed_args.latest_items)
        self.assertEqual(parsed_args.worktreepath, DEFAULT_WORKTREE_PATH)
        self.assertEqual(parsed_args.in_paths, None)
        self.assertEqual(parsed_args.out_paths, None)
        self.assertEqual(parsed_args.entrypoint, None)
        self.assertFalse(parsed_args.details)
        self.assertEqual(parser._backend, Graal)


class TesGraalFunctions(unittest.TestCase):
    """Graal functions tests"""

    def test_find_backends(self):
        backends = graal.graal.find_backends(graal)[0]
        for b in backends.keys():
            self.assertTrue(issubclass(backends.get(b), Graal))


class TestFetch(TestCaseRepo):
    """Unit tests for fetch function"""

    def test_items(self):
        """Test whether a set of items is returned"""

        args = {
            'uri': 'http://example.com/',
            'gitpath': self.git_path,
            'tag': 'test'
        }

        items = graal.graal.fetch(CommandBackend, args, CATEGORY_MOCKED)
        items = [item for item in items]

        self.assertEqual(len(items), 6)
        for i in items:
            self.assertEqual(i['category'], CATEGORY_MOCKED)

    def test_items_multiple_branches(self):
        """Test whether the working tree is created from the first branch in `branches`"""

        args = {
            'uri': 'http://example.com/',
            'gitpath': self.git_path,
            'tag': 'test',
            'branches': ['master', 'v1', 'v2']
        }

        with self.assertLogs(logger, level='WARNING') as cm:
            items = graal.graal.fetch(CommandBackend, args, CATEGORY_MOCKED)
            items = [item for item in items]
            self.assertEqual(cm.output[0], 'WARNING:graal.graal:Only the branch master will be analyzed')

        self.assertEqual(len(items), 6)
        for i in items:
            self.assertEqual(i['category'], CATEGORY_MOCKED)

    def test_items_no_category(self):
        """Test whether a set of items is returned"""

        args = {
            'uri': 'http://example.com/',
            'gitpath': self.git_path,
            'tag': 'test'
        }

        items = graal.graal.fetch(CommandBackend, args, None)
        items = [item for item in items]

        self.assertEqual(len(items), 6)
        for i in items:
            self.assertEqual(i['category'], CATEGORY_MOCKED)

    def test_items_on_error(self):
        """Test whether an exception is thrown when fetching items"""

        args = {
            'uri': 'http://example.com/',
            'gitpath': self.git_path,
            'tag': 'test'
        }

        items = graal.graal.fetch(ErrorCommandBackend, args, CATEGORY_MOCKED)

        with self.assertRaises(Exception):
            _ = [item for item in items]


if __name__ == "__main__":
    unittest.main()
