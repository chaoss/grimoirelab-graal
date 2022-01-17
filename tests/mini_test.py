
from copyreg import constructor
from unicodedata import category
import unittest.mock
from base_repo import TestCaseRepo
from graal.backends.core.cocom import CoCom
import json

from graal.backends.core.cocom.compositions.composition_lizard_file import CATEGORY_COCOM_LIZARD_FILE


# from graal.backends.core.cocom.cocom import CoCom

test_repo = "./tmp/worktree"
test_repo_url = "https://github.com/chaoss/grimoirelab-graal"


class TestMiniTest(TestCaseRepo):

    def constructor(self): 
        print(f'{CoCom.version=}')

        print(f'starting the test with\n{test_repo=}\n{test_repo_url=}')

        cc = CoCom(test_repo_url, test_repo)

        commits = cc.fetch(category=CATEGORY_COCOM_LIZARD_FILE)

        i = 0
        for commit in commits: 
            print(json.dumps(commit, indent=2))
            i += 1
            if i == 2: 
                break



if __name__ == "__main__":
    TestMiniTest().constructor()
    # unittest.main()






