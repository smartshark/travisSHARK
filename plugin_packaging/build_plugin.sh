#!/bin/bash

current=`pwd`
mkdir -p /tmp/travisSHARK/
cp -R ../travisshark /tmp/travisSHARK/
cp ../setup.py /tmp/travisSHARK
cp ../main.py /tmp/travisSHARK
cp * /tmp/travisSHARK/
cd /tmp/travisSHARK/

tar -cvf "$current/travisSHARK_plugin.tar" --exclude=*.tar --exclude=build_plugin.sh --exclude=*/tests --exclude=*/__pycache__ --exclude=*.pyc *
