#!/usr/bin/env python3

import bz2
import argparse


parser = argparse.ArgumentParser()
parser.add_argument("--err", help="Decode and print errlog_file", action="store_true")
parser.add_argument("--std", help="Decode and print stdlog_file", action="store_true")
parser.add_argument("--config", help="Decode and print config_file", action="store_true")
parser.add_argument("--output", help="Decode and print output_file", action="store_true")
args = parser.parse_args()



file = ""

if args.output:
	file = "output"

if args.err:
	file = "errlog"

if args.config:
	file = "config"

if args.std:
	file = "stdlog"

if file:
	print(bz2.decompress(open("Compilations-" + file + "_file.bin","rb").read()).decode())
else:
	parser.print_help()
