#!/bin/bash

for FILE in "$@"
do
    echo "Processing $FILE..."
    fapec -dtype kmall -mt 1 -o /dev/null -ow "$FILE" | grep PredErr | cut -d' ' -f2 > "$FILE.pe"
done