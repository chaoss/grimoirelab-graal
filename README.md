# Graal: a Generic Repository AnALyzer [![Build Status](https://github.com/chaoss/grimoirelab-graal/workflows/build/badge.svg)](https://github.com/chaoss/grimoirelab-graal/actions?query=workflow:build+branch:master+event:push) [![Coverage Status](https://coveralls.io/repos/github/chaoss/grimoirelab-graal/badge.svg?branch=master)](https://coveralls.io/github/chaoss/grimoirelab-graal?branch=master)

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
- [lizard](https://github.com/terryyin/lizard)==1.16.6
- [perceval](https://github.com/chaoss/grimoirelab-perceval)>=0.9.6
- [pylint](https://github.com/PyCQA/pylint)>=1.8.4
- [flake8](https://github.com/PyCQA/flake8)>=3.7.7
- [networkx](https://github.com/networkx/networkx)>=2.1
- [pydot](https://github.com/pydot/pydot)>=1.2.4
- [bandit](https://github.com/PyCQA/bandit)>=1.4.0
- [grimoirelab-toolkit](https://github.com/chaoss/grimoirelab-toolkit)>=0.1.4
- [cloc](http://cloc.sourceforge.net/)
- [scc](https://github.com/boyter/scc)
- [nomos](https://github.com/fossology/fossology/tree/master/src/nomos) 
- [scancode](https://github.com/nexB/scancode-toolkit) 
- [github-linguist](https://github.com/github/linguist)

### How to install/create the executables:
- **Cloc**
  ```
  $> sudo apt-get install cloc
  ```

- **SCC**

A tool similar to cloc - for counting physical the lines of code, blank lines, comment lines, and physical lines of source code in many programming languages and COCOMO estimates written in pure Go.

  ```
  $> go get -u github.com/boyter/scc/
  ```


- **Nomos**

Maybe you'll need to install some packages for compiling the tool.
For example, in Debian, likely you'll need:

```
sudo apt-get install pkg-config libglib2.0-dev libjson-c-dev libpq-dev
```

- For compiling the tool (`nomossa`):

```
$> git clone https://github.com/fossology/fossology
$> cd <...>/fossology/src/nomos/agent
$> make -f Makefile.sa FO_LDFLAGS="-lglib-2.0 -lpq  -lglib-2.0 -ljson-c -lpthread -lrt"
```

- **ScanCode**

```
git clone https://github.com/nexB/scancode-toolkit.git
cd scancode-toolkit
git checkout -b test_scancli 96069fd84066c97549d54f66bd2fe8c7813c6b52
./scancode --help
```

   **Note**: We're now using a clone of scancode-toolkit instead of a release, as the latest release is of 15th February 2019 and the `scancli.py` script (required for execution of scancode_cli) was incroporated later i.e 5th March 2019 and there hasn't been a release since.

- **ScanCode Cli**

After successfully executing the above mentioned steps, (if required) we have to install python modules: `simplejson` and `execnet`, for the execution of `scancode_cli` analyzer.

```
pip install simplejson execnet
```


##  How to install/uninstall
Graal is being developed and tested mainly on GNU/Linux platforms. Thus it is very likely it will work out of the box
on any Linux-like (or Unix-like) platform, upon providing the right version of Python (3.5, 3.6).


**To install**, run:
```
$> git clone https://github.com/chaoss/grimoirelab-graal.git
$> python3 setup.py build
$> python3 setup.py install
```

**To uninstall**, run:
```
$> pip3 uninstall graal
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

Graal can be used from command line or directly from Python, both usages are described below.

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
