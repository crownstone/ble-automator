#!/bin/sh

address="C5:18:C4:52:40:35"
odir="data"
ofile="temp_$address.txt"
ffile="$ofile.filtered"

cd ..
cd $odir

cat $ofile | grep -B1 Temp | grep -v '-' > $ffile
sed -i 's|Temperature: ||g' $ffile
sed -i 's|C$||g' $ffile
sed -i '$!N;s/\n/ /' $ffile


