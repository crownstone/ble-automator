#!/bin/bash

dfu_target="crownstone"

args=""

while getopts "Bt:a:i:vd" optname; do
	case "$optname" in
		"B")
			dfu_target="bootloader_dfu"
			args="$args -B"
			# shift $((OPTIND-1))
			;;
		"t")
			. $BLUENET_CONFIG_DIR/_targets.sh $OPTARG
			# shift $((OPTIND-1))
			;;
		*)
			args="$args -$optname $OPTARG"
			;;
	esac
done

echo "./dfu.py -f $BLUENET_BIN_DIR/$dfu_target.hex $args"
./dfu.py -f $BLUENET_BIN_DIR/$dfu_target.hex $args
