#!/bin/sh

cd /Tuxml;
git fetch;
git checkout dev;
mkdir logs;
./core/tuxml.py /TuxML/linux-4.13.3  | tee logs/output.log;
