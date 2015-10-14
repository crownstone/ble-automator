#!/bin/sh

echo "write to $1.filtered"

# just show all values from the buffer
< $1 cut -f1,4- -d ' ' > $1.filtered

# show all values except for the first (easy) and the last one (hard: complicated sed construct)
#< $1 cut -f1,6- -d ' ' | sed 's/[[:alnum:]]*$//' > $1.filtered
