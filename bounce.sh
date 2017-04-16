#!/usr/bin/env sh

echo "Stopping ..,"
./stopAPRS.sh 2&> /dev/null

echo "Starting ..."
./startAPRS.sh

