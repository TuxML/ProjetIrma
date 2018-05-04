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

## @file tuxml_depML.py
#  @author LE FLEM Erwan
#  @author MERZOUK Fahim
#  @author LEBRETON Mickaël
#  @copyright Apache License 2.0
#  @brief Compilation for analysis of relationship between environment/compilation option and needed dependencies.
#  It can perform compilation, send the result to the database and export the database content to CSV format.abs
#  @details The relevant tables in the database are depML_environnement and packages.
#  @warning For the gathered data to be relevant, you need to start the compilation on an environment where only the amongst
#  minimaliste dependencies are installed. Hence the packages installed by install_default_dependencies() should
#  be uninstalled between two compilations. It is currently not done automaticaly.
#  @todo Add a function remove_default_dependencies() on tuxml_depman.py and a function uninstall_packages(packages) in tuxml_common.py.
#  Then call remove_default_dependencies() before each compilation to handle the warning above.


import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_depman as tdep
import tuxml_environment as tenv
import tuxml as tml
import sys
import MySQLdb
import time
import ast
import csv
import tuxml_argshandler as targs
from itertools import chain

## The CSV file were all the data will be saved
csvfile = open('compilations_details.csv', 'w', newline='', encoding="UTF-8")


## @author MERZOUK Fahim
#  @author LE FLEM Erwan
#  @author LEBRETON Mickael
#
#  @brief perform a compilation and send the result in the database.
def main():
    targs.args_handler()

    # get environment details
    tset.TUXML_ENV = tenv.get_environment_details()

    # get the package manager
    tset.PKG_MANAGER = tcom.get_package_manager()
    if tset.PKG_MANAGER == None:
        sys.exit(-1)

    # updating package database
    if tcom.update_system() != 0:
        sys.exit(-1)

    # install default packages
    if tdep.install_minimal_dependencies() != 0:
        sys.exit(-1)

    tml.gen_config(tset.KCONFIG1)
    launch_compilations()

    # sending data to IrmaDB
    if sendToDB() != 0:
        sys.exit(-1)

    sys.exit(0)


## @author MERZOUK Fahim
#  @author LE FLEM Erwan
#
#  @brief Launch the compilation
def launch_compilations():
        status = -1
        while status == -1:
            missing_packages = []
            missing_files = []

            if tml.compilation() == -1:
                if tml.log_analysis(missing_files, missing_packages) == 0:
                    if tml.install_missing_packages(missing_files, missing_packages) == 0:
                        tcom.pprint(0, "Restarting compilation")
                        status = -1
                    else:
                        status = -3
                else:
                    status = -2
            else:
                status = 0

        if status == 0:
            tcom.pprint(0, "Successfully compiled")
        else:
            tcom.pprint(1, "Unable to compile using this KCONFIG_FILE, status={}".format(status))


## @author LE FLEM Erwan
#  @author MERZOUK Fahim
#
#  @brief Send to the database the result of the compilation.
def sendToDB():
    try:
        socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, "depML_DB")
        cursor = socket.cursor()

        # Values for request
        date = time.gmtime(time.time())
        args_env = {
            "config_file": open(tset.PATH + "/.config", "r").read(),
            "environnement": tset.TUXML_ENV,
        }

        keys   = ",".join(args_env.keys())
        values = ','.join(['%s'] * len(args_env.values()))

        query  = "INSERT INTO depML_environnement({}) VALUES({})".format(keys, values)
        cursor.execute(query, list(args_env.values()))
        socket.commit()
        for missing_file in tdep.tdepLogger.log.keys():
            args_pkg = {
                "cid":cursor.lastrowid,
                "missing_files": str(missing_file),
                "missing_packages": tdep.tdepLogger.log.get(missing_file),
                "candidate_missing_packages": tdep.tdepLogger.candidates.get(missing_file).split(':')[0],
                "resolution_successful":tdep.tdepLogger.status.get(missing_file)
                }
            keys = ",".join(args_pkg.keys())
            values = ','.join(['%s'] * len(args_pkg.values()))
            query  = "INSERT INTO packages({}) VALUES({})".format(keys, values)
            print("QUERY IS: "+query)
            cursor.execute(query, list(args_pkg.values()))

        socket.commit()
        socket.close()

        # file_upload(logfiles, date)

        tcom.pprint(0, "Successfully sent info to db")
        return 0
    except MySQLdb.Error as err:
        tcom.pprint(1, "Can't send info to db : {}".format(err))
        return -1


## @author LE FLEM Erwan
#  @author MERZOUK Fahim
#
#  @brief Change a string in to a dictionary
#
#  @returns A dictionary
def string_to_dict(env_details:str)->dict:
    return eval(env_details)


## @author LE FLEM Erwan,
#  @author MERZOUK Fahim
#
#  @brief retrieve content of the database and export it as a CSV file.
#  @details The CSV file is named "compilations_details.csv" and is located on the
#  current directory.
def write_bdd_to_csv():
        csv_writer = csv.writer(csvfile, delimiter=';', quotechar='|', quoting=csv.QUOTE_MINIMAL)
        try:
            socket = MySQLdb.connect(tset.HOST, tset.DB_USER, tset.DB_PASSWD, "depML_DB")
            query  = "SELECT DISTINCT depML_environnement.config_file,depML_environnement.environnement,packages.missing_files,packages.missing_packages,packages.candidate_missing_packages,packages.resolution_successful FROM packages , depML_environnement WHERE packages.cid=depML_environnement.cid"
            socket.query(query)
            res = socket.store_result()
            tuples = res.fetch_row(maxrows=0)

            first_row = True
            for t in tuples:
                optionName = list() #Column names for compilation options.
                optionValue = list()
                envDict = ast.literal_eval(tuples[0][1])
                #Column names for environment details
                csv_env_col_names = list(chain(*[ list(envDict.keys()) for d in list(envDict.values())]))

                for option in t[0].split('\n'):
                    if '#' in option or len(option.split('=')) < 2:
                        # We ignore the comment lines and the empty lines.
                        continue
                    else:
                        option_name = option.split('=')[0]
                        option_value = option.split('=')[1]
                        #print(option_name+"    " + option_value)
                        if first_row:
                            optionName.append(option_name)
                        optionValue.append(option_value)

                if first_row:
                    #We write the header only once in the first iteration.
                    csv_col_names = optionName + csv_env_col_names
                    csv_col_names.append("missing_files")
                    csv_col_names.append("missing_packages")
                    csv_col_names.append("candidate_missing_packages")
                    csv_col_names.append("resolution_successful")

                    #We write the header here, i.e the column names.
                    csv_writer.writerow(csv_col_names)
                    first_row = False

                #For each column, we write the values.
                csv_col_values = optionValue + list(chain(*[ list(envDict.values()) for d in list(envDict.values())]))
                csv_col_values.append(t[2])
                csv_col_values.append(t[3])
                csv_col_values.append(t[4])
                csv_col_values.append(t[5])
                csv_writer.writerow(csv_col_values)
        except MySQLdb.Error as err:
            tcom.pprint(1, "Can't retrieve info from db : {}".format(err))
            return -1

# ============================================================================ #

if __name__ == '__main__':
    #main()
    # write_bdd_to_csv()
