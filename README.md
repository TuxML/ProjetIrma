# py-scripts

### tuxml.py
    ./tuxml.py source_directory [--debug] [--version]

expected output :

    [*] Cleaning previous compilation
    [*] Generating random config
    [*] Checking dependencies
    [*] Compilation in progress
    [+] Compilation done
    [+] Testing the kernel config
    [+] Successfully compiled in 00:10:45, sending data
    [*] Sending config file and status to database
    [+] Successfully sent info to db


### MLfood.py

Script used to fill the DataBase which "feed" the Machine Learning algorithm.
Allows to start automatically the tuxml.py command on different dockers.

Command should be :

    ./MLfood.py [Integer]

It will start [Integer] number of compilation sequentially.
