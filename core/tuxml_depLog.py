#!/usr/bin/python3

# -*- coding: utf-8 -*-

#   Copyright 2018 TuxML Team
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.

## @file tuxml_depLog.py
#  @author LE FLEM Erwan
#  @author MERZOUK Fahim
#  @brief Log util intented to log the resolving of missing dependencies.
#  For each missing file durring the compilation, we want to log which packages
#  we downloaded to obtains this file.
#  @warning This util is only intended to log the installation of missing packages
#  failing the compilation, not to log the preinstalled package.
#  @copyright Apache License, Version 2.0


import csv
import os
import tuxml_settings as tset


## Key : a missing file, Value : The list of missing package we installed to try
#  to resolve this missing file.
log = dict()


## Key : a missing false, Value : true or false according if we where able to
#  resolve this missing file
status = dict()


## Key : a missing file, Value : Every possible package that contains our missing
#  file.
candidates = dict()


## @author LE FLEM Erwan
#  @author MERZOUK Fahim
#
#  @brief Log the list of all packages that may resolve our dependencie to missing file.
#  @detail The candidates are the list of package we'll install to resolve the dependencie,
#  we stop browsing once we find a suitable package that do not fail the compilation.
#  Hence we not install all candidates packages.
#
#  @param str missing_file a missing file required to compile.
#  @param str missing_packages the list of packages that contains the given missing_file.
def log_candidates_packages(missing_file, missing_packages):
    candidates[missing_file] = missing_packages


## @author LE FLEM Erwan
#  @author MERZOUK Fahim
#
#  @brief Log the installation of the given missing package to solve the dependencie
#  to the given missing file. You should call this function each time you install
#  a missing packages.
#
#  @param str missing_file a missing file required to compile.
#  @param str missing_package a package that we installed while trying to resolve
#  the given missing file.
#
#  @warning You should really call this method in the same order you download the
#  given missing package as the order is relevent.
def log_install(missingFile, missingPackage):
        mapping = log.get(missingFile)
        if (mapping is None):
            mapping = list()
            mapping.append(missingPackage)

        else:
            mapping.append(missingPackage)

        log[missingFile] = mapping


## @author LE FLEM Erwan
#  @author MERZOUK Fahim
#
#  @brief Log the success or the faillure for resolving the given missing file.
#
#  @param str missing_file a missing file required to compile.
#  @param bool True if the resolution has been successfull, else False if we could't
#  find any suitable packages.
def log_status(missingFile, isSuccess):
    status[missingFile] = isSuccess


## author : LE FLEM Erwan
#
#  @brief Export the resolved missing dependancies as a CSV file.
#  @details The export file is tuxml_depLog.csv and is stored in the in the log directory
#  (i.e tset.LOG_DIR)
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


# ============================================================================ #


if __name__ == '__main__':
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
