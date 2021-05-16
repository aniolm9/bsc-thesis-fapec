#!/bin/bash

for FILE in "$@"
do
    CHUNK="4M"
    fapec -dtype kmall -kmopts 0 0 0 -o /dev/null -ow -chunk $CHUNK "$FILE" | grep PredErr | cut -d' ' -f2
done
