

```python
import csv
import MySQLdb
import sys
import os
import subprocess
import genCSV as gc
```


```python
# Class kernel
class kernel:

    def __init__(self, entry):
        self.entry = entry

    def get_cid(self):
        return str(self.entry[0])

    def get_entry(self):
        return self.entry

    def kernel2csv(self):
        try:
            final = list([self.entry[0]] + [str(self.entry[1])] + [str(self.entry[2])] + [self.entry[7]])
            compressed = self.entry[8].split(" , ")
            parse_array = [i.split(" : ") for i in compressed]
            cprss = [fin[1] for fin in parse_array]
            final += cprss

            return final
        except Exception as e:
            #print("Entry len:", len(self.entry))
            print("\n" + str(e))
            exit(-1)
```


```python
# Virtual machine IP adress
HOST            = "148.60.11.195"

## MySQL user
DB_USER         = "script2"

## MySQL password
DB_PASSWD       = "ud6cw3xNRKnrOz6H"
```


```python
# Create a new kernel instance from the physical kernel
def compute_kernel(cid):
    print("\nComputing range of cid...", flush=True)
    kernels_array = []
    
    try:
        socket = MySQLdb.connect(HOST, DB_USER, DB_PASSWD, "IrmaDB_prod")
        cursor = socket.cursor()
        
        for c in cid:
            query = "SELECT * FROM Compilations WHERE cid = %d and incremental_mod = 0" % c
            cursor.execute(query)
            entry = cursor.fetchone()
            
            if entry is not None:
                kernels_array.append(kernel(entry))
    
    except Exception as e:
        print(str(e),"\n" + "Unable to connect to database c = " + str(c), file=sys.stderr)
        exit(-1)
        
    finally:
        cursor.close()
        socket.close()
    
    return kernels_array
```


```python
def create_header():

    conn = MySQLdb.connect(HOST, DB_USER, DB_PASSWD, "IrmaDB_prod")
    cursor = conn.cursor()

    get_prop = "SELECT name, type FROM Properties"
    # Extract properties
    cursor.execute(get_prop)
    types_results = list(cursor.fetchall())

    if len(types_results) == 0:
        print("\nError : Properties not present in database - You need to run Kanalyser first (https://github.com/TuxML/Kanalyser)")

    cursor.close()
    conn.close()

    # .config column names
    names = [""]*len(types_results)
    index = 0
    for (name, typ) in types_results:
        if name not in names:
            names[index] = name
            index += 1

    with open("config_bdd.csv", "w") as f:
        head = ("cid,date,time,vmlinux,GZIP-bzImage,GZIP-vmlinux,GZIP,BZIP2-bzImage,BZIP2-vmlinux,BZIP2,LZMA-bzImage,LZMA-vmlinux,LZMA,XZ-bzImage,XZ-vmlinux,XZ,LZO-bzImage,LZO-vmlinux,LZO,LZ4-bzImage,LZ4-vmlinux,LZ4," + ",".join(names)).split(",")
        writer = csv.DictWriter(f, head)
        writer.writeheader()
```


```python
def to_csv(From, To):    
    values = gc.genCSV(0, From, To, incremental=False)
    
    # Correction for range(From, To) in order to have at least one value
    if From == To:
        To += 1

    cid_array = [c for c in range(From, To)]
    kernels_array = compute_kernel(cid_array)
    
    with open("config_bdd.csv", "a") as csv_file:
        writer = csv.writer(csv_file)
        
        if len(kernels_array) == 1:
            entry_val = kernels_array[0].kernel2csv()
            entry = entry_val + values[0]
            writer.writerow(entry)
        else:

            for num, k in enumerate(kernels_array):
                try:
                    entry_val = k.kernel2csv()
                    entry = entry_val + values[num]
                    #print("value:", values[num][7568])
                    writer.writerow(entry)
                except Exception as e:
                    print("Error at num:", num, flush=True)
                    print(str(e), flush=True)
                    exit(-1)
```


```python
if __name__ == "__main__":
    
    # Change values to append a new range of data from db to the csv
    From = 62000 # 40510 56580 # 
    To = 92800 #88036 #80054 # 78900 # 56593 # 
    
    subprocess.run("rm config_bdd.csv", shell=True)
    
    if not os.path.exists("config_bdd.csv"):
        create_header()
        print("config_bdd.csv created", flush=True)
    
    print("From %d to %d" % (From, To))
    to_csv(From, To)
    print("\nWritten!")
    
    """
    with open("config_bdd.csv", "r") as file:
        t = file.readlines()
        lines = []
        for i in range(len(t)):
            lines.append(t[i].split(","))
    """

    
```

    config_bdd.csv created
    From 62000 to 92800
    Connecting to db IrmaDB_prod at 148.60.11.195...Done
    Filling rows :
    Progression: [####################] 100%
    
    Computing range of cid...
    
    Written!



```python
import bz2

def print_logs_configurations(cid):
    print("Printing logs of cid=", cid)
    
    try:
        socket = MySQLdb.connect(HOST, DB_USER, DB_PASSWD, "IrmaDB_prod")
        cursor = socket.cursor()

        query = "SELECT stdlog_file, errlog_file, output_file FROM Compilations WHERE cid = %d" % cid
        cursor.execute(query)
        stdlog_file, errlog_file, output_file = cursor.fetchone()
            
        if (stdlog_file is None) or (errlog_file is None) or (output_file is None):
            print ("Unable to retrieve cid...")
            return
        
        print("STD LOG FILE")
        print(bz2.decompress(stdlog_file).decode('ascii'))
        print("#########")
        print("ERR LOG FILE")
        print("#########")
        print(bz2.decompress(errlog_file).decode()) # not ascii? 
        print("#########")
        print("OUTPUT LOG FILE")
        print("#########")
        print(bz2.decompress(output_file).decode('ascii'))
    
    except Exception as e:
        print(str(e),"\n" + "Unable to connect to database c = " + str(c), file=sys.stderr)
        exit(-1)
        
    finally:
        cursor.close()
        socket.close()

#print_logs_configurations(76319) #78749: WANXL_BUILD_FIRMWARE # 79052 AIC7XXX_BUILD_FIRMWARE
```
