#!/usr/bin/python3
import csv
import os
import tuxml_settings as tset

# Log util intented to log the resolving of missing dependencies.
# For each missing file durring the compilation, we want to log which packages we
# downloaded to obtains this file.
#
# This util is only intended to log the installation of missing packages failing the compilation,
# not to log the preinstalled package.

log = dict()
status = dict()
candidates = dict()

def log_candidates_packages(missing_file, missing_packages):
    candidates[missingFile] = missing_packages

# Log the installation of the given missing package to solve the dependencie to the given missing file.
# You should really call this method in the same order you download the given missing package as the order is relevent.

def log_install(missingFile, missingPackage):
        mapping = log.get(missingFile)
        if (mapping is None):
            mapping = list()
            mapping.append(missingPackage)

        else:
            mapping.append(missingPackage)

        log[missingFile] = mapping


# Log the success or the faillure for resolving the given missing file.


def log_status(missingFile, isSuccess):
    status[missingFile] = isSuccess


# author : LE FLEM Erwan
#
# Export the resolved missing dependancies as a CSV file.
#
# The export file is tuxml_depLog.csv and is stored in the in the log directory
# (i.e tset.LOG_DIR)


def export_as_csv():

    if not os.path.exists(tset.PATH + tset.LOG_DIR):
        os.makedirs(tset.PATH + tset.LOG_DIR)

    with open(tset.PATH + tset.LOG_DIR + '/tuxml_depLog.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, ("Missing files encountered", "Missing packages installed","Resolution successfull"))
        writer.writeheader()
        for k in log.keys():
            if status.get(k) is None:
                status[k] = True
            writer.writerow({"Missing files encountered" : k, "Missing packages installed" : log[k], "Resolution successfull":status[k]})


# test code
def main():
    # While testing, we export the file in core directory.
    tset.PATH = os.path.dirname(os.path.abspath( __file__ ))
    log_install("FIle1", "missingPackage1")
    log_install("FIle1", "missingPackage11")
    log_status("FIle1", False)
    log_install("FIle2", "missingPackage2")
    log_status("FIle2", True)
    log_install("FIle3", "missingPackage3")
    log_install("FIle3", "missingPackage4")
    log_install("FIle3", "missingPackage5")
    log_status("FIle3", True)
    log_install("FIle6", "missingPackage6")
    log_status("FIle6", False)
    log_install("FIle1000", "missingPackage1000_1")
    log_install("FIle1000", "missingPackage1000_1")
    log_status("FIle1000", True)
    export_as_csv()


if __name__ == '__main__':
    main()
