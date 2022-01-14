#!/bin/bash

# Standard stuff
sudo apt-get update
sudo apt-get upgrade

# Install go
curl -O https://storage.googleapis.com/golang/go1.13.5.linux-amd64.tar.gz
tar -xvf ./go1.13.5.linux-amd64.tar.gz 
sudo mv go /usr/local
sudo ln -s /usr/local/go/bin/go /usr/local/bin/go

CURDIR=`pwd`
cd $HOME
# Programs used by graal
    # SCC
    go get -u github.com/boyter/scc/
    sudo ln -s $HOME/go/bin/scc /usr/local/bin/scc

    # Cloc
    sudo apt-get install cloc

    # Nomos
    sudo apt-get install pkg-config libglib2.0-dev libjson-c-dev libpq-dev
    git clone https://github.com/fossology/fossology
    cd ./fossology/src/nomos/agent
    make -f Makefile.sa FO_LDFLAGS="-lglib-2.0 -lpq  -lglib-2.0 -ljson-c -lpthread -lrt"
    cd $HOME

    # Scancode
    git clone https://github.com/nexB/scancode-toolkit.git
    cd scancode-toolkit
    git checkout -b test_scancli 96069fd84066c97549d54f66bd2fe8c7813c6b52
    ./scancode --help
    pip install simplejson execnet
    cd $HOME

cd $OLDDIR
# Install graal dependencies
sudo pip install -r ./requirements.txt 

echo "export PYTHONPATH=`pwd`"
