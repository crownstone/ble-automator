#!/bin/sh

iface=${1:? "Interface argument missing"}
address=${2:? "Address argument missing"}

odir="data"
ofile="temp_$address.txt"

cd ..

mkdir -p $odir

echo $(date +"%s") >> "$odir/$ofile"
./getTemperature.py -i $iface -a $address | grep Temperature >> $odir/$ofile
