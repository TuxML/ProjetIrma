#!/bin/bash

isFound=false
pid='ps -a | grep qemu'

while [ egrep "Boot took|Kernel panic" log.txt ];
do
	
done

if [ grep "Boot took" log.txt -eq 1 ]; then
	echo 'grep "Boot took" log.txt'
elif [ grep "Kernel panic" -eq 1 ]; then
	echo "Kernel panic"
else 
   	echo "Error" 
fi

kill -9 $pid

