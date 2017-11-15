# py-scripts

## tuxml.py
```
[*] USE : sudo ./tuxml.py </path/to/sources/directory> [option1 option2 ...]
[*] Available options :
        -d  --debug             TuxML is more verbose
        -h  --help              Print this
            --no-randconfig     Do not generate a new config file
        -v  --version           Display the version of TuxML
```

Expected output :

```
[*] Cleaning previous compilation
[*] Generating random config
[*] Checking dependencies
[*] Compilation in progress
[+] Compilation done
[+] Testing the kernel config
[+] Successfully compiled in 00:10:45, sending data
[*] Sending config file and status to database
[+] Successfully sent info to db
```

## MLfood.py

Script used to fill the DataBase which "feed" the Machine Learning algorithm.
Allows to start automatically the tuxml.py command on different dockers.

Command should be :

    ./MLfood.py [Integer]

It will start [Integer] number of compilation sequentially.
