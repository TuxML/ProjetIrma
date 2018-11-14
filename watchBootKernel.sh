#!/bin/bash

isFound=false
time=300
pid='ps -a | grep qemu'

while[ egrep "Boot took|Kernel panic" log.txt || $time -gt 0 ]
   $time--
done

if[ $time -eq 0 ]; then 
   	echo "Boot too long"
elif [ grep "Boot took" log.txt -eq 1 ]; then
	echo 'grep "Boot took" log.txt'
elif [ grep "Kernel panic" -eq 1 ]; then
	echo "Kernel panic"
else 
   	echo "Error" 
fi

kill -9 $pid

