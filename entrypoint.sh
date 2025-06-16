#!/bin/bash


PYTHON=$(python --version | tr -d 'Python ');

get_mallet() {
    wget https://mallet.cs.umass.edu/dist/mallet-2.0.8.tar.gz
    tar -xvzf mallet-2.0.8.tar.gz
    mv mallet-2.0.8 LID_tool/
    rm -rf mallet-2.0.8.tar.gz
    rm ._mallet-2.0.8
}

if [[ $PYTHON == 3.9.* ]]; then
    cd app
    if [ $(basename `pwd`) == 'app' ]; then
    #get_mallet
    pip install -r requirements.txt
    cd indic-trans
        if [ $(basename `pwd`) == 'indic-trans' ]; then
            pip install -r requirements.txt
            pip install .
            cd /
        else
            echo "Current directory not indic-trans, try again."
            echo "Exiting..."
            exit
        fi
    else
        echo "Current directory not app, try again."
        echo "Exiting..."
        exit
    fi
else
    echo "This program needs Python version 3.9.*"
    echo "Your current Python version is $PYTHON. Please try again."
fi