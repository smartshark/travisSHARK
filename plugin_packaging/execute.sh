#!/bin/sh
PLUGIN_PATH=$1

COMMAND="python3.5 $1/main.py --db-database $4 --db-hostname $5 --db-port $6 --url $9"
if [ ! -z ${2} ] && [ ${2} != "None" ]; then
	COMMAND="$COMMAND --db-user ${2}"
fi

if [ ! -z ${3} ] && [ ${3} != "None" ]; then
	COMMAND="$COMMAND --db-password ${3}"
fi

if [ ! -z ${7} ] && [ ${7} != "None" ]; then
	COMMAND="$COMMAND --db-authentication ${7}"
fi

if [ ! -z ${8} ] && [ ${8} != "None" ]; then
    COMMAND="$COMMAND --ssl"
fi

if [ ! -z ${10} ] && [ ${10} != "None" ]; then
    COMMAND="$COMMAND --proxy-host ${10}"
fi

if [ ! -z ${11} ] && [ ${11} != "None" ]; then
	COMMAND="$COMMAND --proxy-port ${11}"
fi

if [ ! -z ${12} ] && [ ${12} != "None" ]; then
	COMMAND="$COMMAND --proxy-password ${12}"
fi

if [ ! -z ${13} ] && [ ${13} != "None" ]; then
    COMMAND="$COMMAND --proxy-user ${13}"
fi

if [ ! -z ${14} ] && [ ${14} != "None" ]; then
    COMMAND="$COMMAND --debug ${14}"
fi

if [ ! -z ${15} ] && [ ${15} != "None" ]; then
    COMMAND="$COMMAND --token ${15}"
fi

if [ ! -z ${16} ] && [ ${16} != "None" ]; then
    COMMAND="$COMMAND --ignore-errors"
fi

if [ ! -z ${17} ] && [ ${17} != "None" ]; then
    COMMAND="$COMMAND --only-failed"
fi

if [ ! -z ${18} ] && [ ${18} != "None" ]; then
    COMMAND="$COMMAND --rerun"
fi

$COMMAND