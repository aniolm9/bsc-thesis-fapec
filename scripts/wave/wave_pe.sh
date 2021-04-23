#!/bin/bash

for FILE in "$@"
do
    ORDER=10
    BLEN=1024
    CHUNK=8M
    PERLEN=65536
    TRNLEN=65536
    fapec -dtype 16 -signed -chunk $CHUNK -bl $BLEN -wave $ORDER 2 0 0 -per $PERLEN -trn $TRNLEN -o /dev/null -ow "$FILE" | grep PredErr | cut -d' ' -f2
done
