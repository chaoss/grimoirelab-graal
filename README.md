# Graal: a Generic Repository AnALyzer [![Build Status](https://github.com/chaoss/grimoirelab-graal/workflows/tests/badge.svg)](https://github.com/chaoss/grimoirelab-graal/actions?query=workflow:tests+branch:master+event:push) [![Coverage Status](https://coveralls.io/repos/github/chaoss/grimoirelab-graal/badge.svg?branch=master)](https://coveralls.io/github/chaoss/grimoirelab-graal?branch=master)  [![PyPI version](https://badge.fury.io/py/graal.svg)](https://badge.fury.io/py/graal)

Graal leverages on the Git backend of [Perceval](https://github.com/chaoss/grimoirelab-perceval) and enhances it to set up ad-hoc
source code analysis. Thus, it fetches the commits from a Git repository and provides a mechanism to plug third party tools/libraries focused on source code analysis.

## How it works
The Perceval Git backend creates a local mirror of a Git repository (local or remote), fetches the metadata of commits in chronological order and returns them as a list of JSON documents
(one per commit). Graal leverages on the incremental functionalities provided by the Git backend and enhances the logic to handle Git repositories by creating a
working tree to perform checkout operations (which are not possible on a Git mirror). Graal intercepts each JSON document and enables the user to perform the following steps:
- **Filter.** The filtering is used to select or discard commits based on the information available in the JSON document and/or via the Graal parameters. For any selected commit,
Graal executes a checkout on the working tree using the commit hash, thus setting the state of the working tree at that given revision.
- **Analyze.** The analysis takes the JSON document and the current working tree and enables the user to set up ad-hoc source code analysis by plugging existing tools through system calls
or their Python interfaces, when possible. The results of the analysis are parsed and manipulated by the user and then automatically embedded in the JSON document. It is worth
noting that in this step the user can rely on some predefined functionalities of Graal to deal with the repository snapshot (e.g., listing files, creating archives).
- **Post-process.** In the final step, the inflated JSON document can be optionally processed to alter (e.g., renaming, removing) its attributes, thus granting the user complete control over the output of Graal executions.

Several parameters (inherited from the [Git backend](http://perceval.readthedocs.io/en/latest/perceval.backends.core.html#module-perceval.backends.core.git)) are available to control the execution; for instance, **from_date** and **to_date**
allow to select commits authored since and before a given date, **branches** allows to fetch commits only from specific branches,
and **latest_items** returns only those commits which are new since the last fetch operation. Graal includes additional parameters to drive
the analysis to filter in/out files and directories in the repository (**in_paths** and **out_paths**), set the **entrypoint**
and define the **details** level of the analysis (useful when analyzing large software projects).

## Requirements


 * Python >= 3.8
 * Poetry >= 1.2
 * [github-linguist](https://github.com/github/linguist)
 * [FOSSology](https://github.com/fossology/fossology)
 * [cloc](https://github.com/AlDanial/cloc)
 * [scc](https://github.com/boyter/scc)
 * [ScanCode toolkit](https://github.com/nexB/scancode-toolkit)
 * [crossJadoLint](https://github.com/crossminer/crossJadolint/)

You will also need some other Python libraries for running the tool, you can find the
whole list of dependencies in [pyproject.toml](pyproject.toml) file.

### How to install and create the executables:
- **github-linguist**
 
  Library is used to detect blob languages, ignore binary or vendored files, suppress generated files in diffs, and generate language breakdown graphs.
  ```
  $ gem install github-linguist -v 7.15
  ```
- **FOSSology**

  Open source license compliance software system and toolkit. You can run license, copyright, and export control scans from the command line.
  ```
  $ wget https://github.com/fossology/fossology/releases/download/3.11.0/FOSSology-3.11.0-ubuntu-focal.tar.gz
  $ tar -xzf FOSSology-3.11.0-ubuntu-focal.tar.gz
  $ sudo apt-get -y install ./packages/fossology-common_3.11.0-1_amd64.deb \
                            ./packages/fossology-nomos_3.11.0-1_amd64.deb
  ```

- **Cloc**

  Count blank lines, comment lines, and physical lines of source code in many programming languages.
  ```
  $ sudo apt-get install cloc
  ```

- **SCC**

  A tool similar to cloc - for counting physical the lines of code, blank lines, comment lines, and physical lines of source code in many programming languages and COCOMO estimates written in pure Go.
  ```
  $ go install github.com/boyter/scc@latest
  ```

- **ScanCode Toolkit**

  ScanCode detects licenses, copyrights, package manifests & dependencies and more by scanning code.
  ```
  $ mkdir exec
  $ cd exec
  $ git clone https://github.com/nexB/scancode-toolkit.git
  $ cd scancode-toolkit
  $ git checkout -b test_scancli 96069fd84066c97549d54f66bd2fe8c7813c6b52
  $ ./scancode --help
  ```

  *Note: We're now using a clone of scancode-toolkit instead of a release, as the latest release is of 15th February 2019 and the `scancli.py` script (required for execution of scancode_cli) was incorporated later i.e 5th March 2019 and there hasn't been a release since.*

- **crossJadolint**

  This is a Dockerfile linter tool, implemented in Java and essentialy is a port of Hadolint (Haskell Dockerfile Linter)
  ```
  $ cd exec
  $ wget https://github.com/crossminer/crossJadolint/releases/download/Pre-releasev2/jadolint.jar
  ```

## Installation

There are several ways to install Graal on your system: packages or source 
code using Poetry or pip.

### PyPI

Graal can be installed using pip, a tool for installing Python packages. 
To do it, run the next command:
```
$ pip install graal
```

### Source code

To install from the source code you will need to clone the repository first:
```
$ git clone https://github.com/chaoss/grimoirelab-graal
$ cd grimoirelab-graal
```

Then use pip or Poetry to install the package along with its dependencies.

#### Pip
To install the package from local directory run the following command:
```
$ pip install .
```
In case you are a developer, you should install graal in editable mode:
```
$ pip install -e .
```

#### Poetry
We use [poetry](https://python-poetry.org/) for dependency management and 
packaging. You can install it following its [documentation](https://python-poetry.org/docs/#installation).
Once you have installed it, you can install graal and the dependencies in 
a project isolated environment using:
```
$ poetry install
```
To spaw a new shell within the virtual environment use:
```
$ poetry shell
```

## Backends
Several backends have been developed to assess the genericity of Graal. Those backends leverage on source code analysis
tools, where executions are triggered via system calls or their Python interfaces. In the current status, the backends
mostly target Python code, however other backends can be easily developed to cover other programming languages. The
currently available backends are:
- **CoCom** gathers data about code complexity (e.g., cyclomatic complexity, LOC) from projects written in popular programming languages such as: C/C++, Java, Scala, JavaScript, Ruby, Python, Lua and Golang. It leverages on [Cloc](http://cloc.sourceforge.net/), [Lizard](https://github.com/terryyin/lizard) and [scc](https://github.com/boyter/scc). The tool can be exectued at `file` and `repository` levels activated with the help of category: `code_complexity_lizard_file` or `code_complexity_lizard_repository`.
- **CoDep** extracts package and class dependencies of a Python module and serialized them as JSON structures, composed of edges and nodes, thus easing the bridging with front-end technologies for graph visualizations. It combines [PyReverse](https://pypi.org/project/pyreverse/) and [NetworkX](https://networkx.github.io/).
- **CoQua** retrieves code quality insights, such as checks about line-code’s length, well-formed variable names, unused imported modules and code clones. It uses [PyLint](https://www.pylint.org/) and [Flake8](http://flake8.pycqa.org/en/latest/index.html). The tools can be activated by passing the corresponding category: `code_quality_pylint` or `code_quality_flake8`.
- **CoVuln** scans the code to identify security vulnerabilities such as potential SQL and Shell injections, hard-coded passwords and weak cryptographic key size. It relies on [Bandit](https://github.com/PyCQA/bandit).
- **CoLic** scans the code to extract license & copyright information. It currently supports [Nomos](https://github.com/fossology/fossology/tree/master/src/nomos) and [ScanCode](https://github.com/nexB/scancode-toolkit). They can be activated by passing the corresponding category: `code_license_nomos`, `code_license_scancode`, or `code_license_scancode_cli`.
- **CoLang** gathers insights about code language distribution of a git repository. It relies on [Linguist](https://github.com/github/linguist) and [Cloc](http://cloc.sourceforge.net/) tools. They can be activated by passing the corresponding category: `code_language_linguist` or `code_language_cloc`.

### How to develop a backend
Creating your own backend is pretty easy, you only need to redefine the following methods of Graal:
- **_filter_commit.** This method is used to select or discard commits based on the information available in the JSON document
and/or via the Graal parameters (e.g., the commits authored by a given user or targeting a given software component).
For any selected commit, Graal executes a checkout on the working tree using the commit hash, thus setting the state of
the working tree at that given revision.
- **_analyze.** This method takes the document and the current working tree and allows to connect existing tools through system calls or their Python interfaces, when possible.
The results of the analysis, parsed and manipulated by the user, are automatically embedded in the JSON document.
- **_post.** This method allows to alter (e.g., renaming, removing) the attributes of the inflated JSON documents.

## How to use

### From command line
Launching Graal from command line does not require much effort, but only some basic knowledge of GNU/Linux shell commands.

The example below shows how easy it is to fetch code complexity information from a Git repository. The **CoCom** backend
requires the URL where the repository is located (_https://github.com/chaoss/grimoirelab-perceval_) and the local path
where to mirror the repository (_/tmp/graal-cocom_). Then, the JSON documents produced are redirected to the file _graal-cocom.test_.

- **CoCom Backend**

```
$ graal cocom https://github.com/chaoss/grimoirelab-perceval --git-path /tmp/graal-cocom > /graal-cocom.test
Starting the quest for the Graal.
Git worktree /tmp/... created!
Fetching commits: ...
Git worktree /tmp/... deleted!
Fetch process completed: .. commits inspected
Quest completed.
```

- **CoLic Backend**

```
graal colic https://github.com/chaoss/grimoirelab-toolkit --git-path /tmp/scancode_cli --exec-path /home/scancode-toolkit/etc/scripts/scancli.py --category code_license_scancode_cli
Starting the quest for the Graal.
Git worktree /tmp/... created!
Fetching commits: ...
Git worktree /tmp/... deleted!
Fetch process completed: .. commits inspected
Quest completed.
```

In the above example, we're using scancode_cli analyzer. Similarly, we can use the scancode analyzer by providing the category as `code_license_scancode` and it's corresponding executable path.

### From Python
Graal’s functionalities can be embedded in Python scripts. Again, the effort of using Graal is minimum. In this case the user
only needs some knowledge of Python scripting. The example below shows how to use Graal in a script.

The **graal.backends.core.cocom** module is imported at the beginning of the file, then the **repo_uri** and **repo_dir** variables
are set to the URI of the Git repository and the local path where to mirror it. These variables are used to initialize a
**CoCom class object**. In the last line of the script, the commits inflated with the result of the analysis are retrieved
using the fetch method. The fetch method inherits its argument from **Perceval**, thus it optionally accept two Datetime
objects to gather only those commits after and before a given date, a list of branches to focus on specific development
activities, and a flag to collect the commits available after the last execution.

```
#! /usr/bin/env python3
from graal.backends.core.cocom import CoCom

# URL for the git repo to analyze
repo_uri = ’http://github.com/chaoss/grimoirelab-perceval’

# directory where to mirror the repo
repo_dir = ’/tmp/graal-cocom’

# Cocom object initialization
cc = CoCom(uri=repo_uri, git_path=repo_dir)

# fetch all commits
commits = [commit for commit in cc.fetch()]
```

## How to integrate it with Arthur
[Arthur](https://github.com/chaoss/grimoirelab-kingarthur) is another tool of the [Grimoirelab ecosystem](https://chaoss.github.io/grimoirelab/). It was originally designed to allow to schedule
and run Perceval executions at scale through distributed **Redis** queues, and store the obtained results in an **ElasticSearch** database.

Arthur has been extended to allow handling Graal tasks, which inherit from Perceval Git tasks. The code to make this extension possible is
available at: https://github.com/chaoss/grimoirelab-kingarthur/pull/33.

Information about Arthur is available at https://github.com/chaoss/grimoirelab-kingarthur.
