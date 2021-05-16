#!/bin/bash

for FILE in "$@"
CHUNK=4M
do
    fapec -dtype kmall -kmopts 0 0 0 -o /dev/null -ow -chunk $CHUNK "$FILE" | grep PredErr | cut -d' ' -f2
done
