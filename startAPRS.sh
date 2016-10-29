#!/usr/bin/env sh
export PGM="DecodeMessages.py"
export CMD=$HOME/PythonDev/pyaprs/pyaprs/$PGM
export LOGS=$HOME/logs/$PGM.log
source $HOME/PythonDev/pyaprs/bin/activate
nohup $CMD > $LOGS 2>&1 &
tail -f $LOGS
