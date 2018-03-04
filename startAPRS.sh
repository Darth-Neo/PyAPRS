#!/usr/bin/env sh
~/bin/startMongoDB.sh
export PGM="DecodeMessages.py"
export CMD=$HOME/PythonDev/pyaprs/pyaprs/$PGM
export LOGS=$HOME/logs/$PGM.log
source $HOME/PythonDev/pyaprs/bin/activate
nohup $CMD > $LOGS 2>&1 &
echo Tailing $LOGS
tail -f $LOGS
