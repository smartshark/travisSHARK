#!/bin/sh
PLUGIN_PATH=$1
cd $PLUGIN_PATH

# Install travisSHARK
python3.5 $PLUGIN_PATH/setup.py install --user