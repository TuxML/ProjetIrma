
#!/bin/bash

var=1
echo "Scan running"

while [[ $var -eq "1" ]];
do
        tmp=$(egrep 'Boot took|Kernel panic' root/kdev/log.txt)
        var=$?
done

if [[ $var -gt "1" ]]; then
        echo "Error"
else 
        echo $tmp 
fi

kill -9 $(pgrep qemu)

