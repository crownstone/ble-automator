#!/bin/sh

echo "write to $1.filtered"
< $1 cut -f1,6- -d ' ' | sed 's/[[:alnum:]]*$//' > $1.filtered
