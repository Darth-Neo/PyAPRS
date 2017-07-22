#!/usr/bin/env sh
export PGM="DecodeMessages.py"
echo "Checking " $PGM
export CMD=$HOME/PythonDev/pyaprs/pyaprs/$PGM
echo $(ps aux | grep $PGM | awk '{print $2}' | head -n 1) 
