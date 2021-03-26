#!/bin/bash

for FILE in "$@"
do
    echo "Processing $FILE..."
    FAPEC="/home/aniol/Devel/Dapcom/fapec/fapec"
    ORDER=4
    PERLEN=8192
    SIZE=$(stat --printf="%s" "$FILE")

    let m=$PERLEN/2+$ORDER
    let lastPer=$SIZE%$PERLEN/4+1
    let line=$lastPer+$ORDER-1

    $FAPEC -dtype 16 -signed -wave $ORDER 2 0 0 -per $PERLEN -mt 1 -o /dev/null "$FILE" | grep PredErr | awk -v order="$ORDER" -v m="$m" '(NR-1)%m > order-1' | cut -d' ' -f2 | sed 1,22d | tac | sed ${lastPer},${line}d | tac > "$FILE.pe"
done
