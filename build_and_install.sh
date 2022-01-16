
rm -r ./tmp/worktree
sudo pip3 uninstall graal
python3 setup.py build
sudo python3 setup.py install

python3 tests/mini_test.py
