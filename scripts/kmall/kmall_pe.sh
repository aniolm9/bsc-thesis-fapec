#!/bin/bash

for FILE in "$@"
do
    fapec -dtype kmall -o /dev/null -ow "$FILE" | grep PredErr | cut -d' ' -f2
done
