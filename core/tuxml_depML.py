import tuxml_sendDB as tsen
import tuxml_common as tcom
import tuxml_settings as tset
import tuxml_depman as tdep
import tuxml_environment as tenv
import tuxml as tml
import sys
import MySQLdb
import time
import tuxml_depLog as tdepl
import tuxml_argshandler as targs

# author : LEBRETON Mickael
#
# Main function
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

    launch_compilations()

    # sending data to IrmaDB
    if sendToDB() != 0:
        sys.exit(-1)

    sys.exit(0)

def launch_compilations():
        # launching compilation
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

        for missing_file in tdep.tdepLogger.log.keys():
            args_pkg = {
                "cid":cursor.lastrowid,
                "missing_files": str(missing_file),
                "missing_packages": str(tdep.tdepLogger.log.get(missing_file)),
                "resolution_successful":tdep.tdepLogger.status.get(missing_file)
            }
            keys   = ",".join(args_pkg.keys())
            values = ','.join(['%s'] * len(args_pkg.values()))
            query  = "INSERT INTO packages({}) VALUES({})".format(keys, values)
            cursor.execute(query, list(args_pkg.values()))

        socket.commit()
        socket.close()

        # file_upload(logfiles, date)

        tcom.pprint(0, "Successfully sent info to db")
        return 0
    except MySQLdb.Error as err:
        tcom.pprint(1, "Can't send info to db : {}".format(err))
        return -1

# ============================================================================ #

if __name__ == '__main__':
    main()
