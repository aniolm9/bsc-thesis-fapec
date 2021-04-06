#!/bin/bash

for FILE in "$@"
do
    ORDER=8
    PERLEN=4096
    TRNLEN=4096
    fapec -dtype 16 -signed -wave $ORDER 2 0 0 -per $PERLEN -trn $TRNLEN -o /dev/null -ow "$FILE" | grep PredErr | cut -d' ' -f2
done
