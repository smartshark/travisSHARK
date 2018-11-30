#!/bin/sh
PLUGIN_PATH=$1

COMMAND="python3.5 $1/main.py --project_name ${2} --db-database $5 --db-hostname $6 --db-port $7 --repository-url ${10}"
if [ ! -z ${3} ] && [ ${3} != "None" ]; then
	COMMAND="$COMMAND --db-user ${3}"
fi

if [ ! -z ${4} ] && [ ${4} != "None" ]; then
	COMMAND="$COMMAND --db-password ${4}"
fi

if [ ! -z ${8} ] && [ ${8} != "None" ]; then
	COMMAND="$COMMAND --db-authentication ${8}"
fi

if [ ! -z ${9} ] && [ ${9} != "None" ]; then
    COMMAND="$COMMAND --ssl"
fi

if [ ! -z ${11} ] && [ ${11} != "None" ]; then
    COMMAND="$COMMAND --proxy-host ${11}"
fi

if [ ! -z ${12} ] && [ ${12} != "None" ]; then
	COMMAND="$COMMAND --proxy-port ${12}"
fi

if [ ! -z ${13} ] && [ ${13} != "None" ]; then
	COMMAND="$COMMAND --proxy-password ${13}"
fi

if [ ! -z ${14} ] && [ ${14} != "None" ]; then
    COMMAND="$COMMAND --proxy-user ${14}"
fi

if [ ! -z ${15} ] && [ ${15} != "None" ]; then
    COMMAND="$COMMAND --debug ${15}"
fi

if [ ! -z ${16} ] && [ ${16} != "None" ]; then
    COMMAND="$COMMAND --token ${16}"
fi

if [ ! -z ${17} ] && [ ${17} != "None" ]; then
    COMMAND="$COMMAND --ignore-errors"
fi

if [ ! -z ${18} ] && [ ${18} != "None" ]; then
    COMMAND="$COMMAND --only-failed"
fi

if [ ! -z ${19} ] && [ ${19} != "None" ]; then
    COMMAND="$COMMAND --rerun"
fi

$COMMAND