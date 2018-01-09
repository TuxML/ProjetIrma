#!/bin/sh

cd /TuxML;
git fetch;
git checkout dev;
mkdir logs;
./core/tuxml.py linux-4.13.3/ | tee logs/output.log;
