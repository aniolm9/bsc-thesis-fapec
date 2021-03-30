#!/bin/bash

for FILE in "$@"
do
    echo "Processing $FILE..."
    ORDER=4
    PERLEN=8192
    : '
    SIZE=$(stat --printf="%s" "$FILE")
    let LINES=$SIZE/2-22

    let m=$PERLEN/2+$ORDER
    let bool=$SIZE%$PERLEN
    if [[ $bool -ne 0 ]]; then
        bool=1
    fi
    let firstLPC="($LINES-$SIZE%$PERLEN/4+1)*$bool"
    let lastLPC="$firstLPC+($ORDER-1)*$bool"
    '
    #fapec -dtype 16 -signed -wave $ORDER 2 0 0 -per $PERLEN -mt 1 -o /dev/null -ow "$FILE" | grep PredErr | awk -v order="$ORDER" -v m="$m" '(NR-1)%m > order-1' | cut -d' ' -f2 | sed 1,22d | sed ${firstLPC},${lastLPC}d > "$FILE.pe"
    fapec -dtype 16 -signed -wave $ORDER 2 0 0 -per $PERLEN -o /dev/null -ow "$FILE" | grep PredErr | cut -d' ' -f2
done
