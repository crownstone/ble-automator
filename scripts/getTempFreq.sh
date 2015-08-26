#!/bin/sh

address="C5:18:C4:52:40:35"
iface="hci0"
freq=60
freq=5

command="./getTemp.sh $iface $address"
watch --interval $freq $command
