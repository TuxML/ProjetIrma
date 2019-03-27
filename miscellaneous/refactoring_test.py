#!/usr/bin/python3

import argparse
import bz2
import subprocess
import MySQLdb
from time import time, sleep
import os
import shutil

__IP_BDD = "148.60.11.195"
__USERNAME_BDD = "csvgen"
__PASSWORD_USERNAME_BDD = "yHGE0Km4bxxKoYdb"
__PROD_BDD = "IrmaDB_prod"
__RESULT_BDD = "IrmaDB_result"


## fetch_cursor_to_database
# @author Picard Michaël
# @version 1
# @brief Connect yourself to your database, and return a cursor on it.
def fetch_cursor_to_database(host, user, password, database_name):
    return MySQLdb.connect(
        host=host,
        user=user,
        passwd=password,
        db=database_name
    ).cursor()


## select_fields_with_where_equal_condition
# @author PICARD Michaël
# @version 1
# @brief Retrieve result from database following SELECT FROM WHERE = statement.
# @param field_list If an empty list, select all field. If not, select the given
# field.
# @param where_directory If an empty directory, select all. If not, select with
# given condition(s).
# @return A tuple containing all the result.
def select_fields_with_where_equal_condition(cursor, field_list, table_name,
                                             cond_where_directory):
    field_to_select = "*"
    if len(field_list):
        field_to_select = ", ".join(field_list)

    where_condition = ""
    argument_query = list()
    if not(len(field_list)):
        where_condition = "1"
    else:
        for k, v in cond_where_directory.items():
            where_condition = "{}{}=%s and ".format(where_condition, k)
            argument_query.append(v)
        where_condition = where_condition[:-5]

    query_select = "SELECT {} FROM {} WHERE {}".format(
        field_to_select, table_name, where_condition)
    cursor.execute(query_select, argument_query)
    return cursor.fetchall()


def get_config_from_database_prod(cid):
    cursor = fetch_cursor_to_database(
        __IP_BDD, __USERNAME_BDD, __PASSWORD_USERNAME_BDD, __PROD_BDD)
    result = select_fields_with_where_equal_condition(
        cursor, ['config_file'], 'Compilations',
        {'cid': cid, 'incremental_mod': 0})
    if not len(result):
        raise ValueError("The cid {} doesn't exist in the "
                         "database or correspond to an incremental "
                         "compilation.".format(cid))
    return bz2.decompress(result[0][0]).decode()


def get_size_from_database_prod(cid):
    cursor = fetch_cursor_to_database(
        __IP_BDD, __USERNAME_BDD, __PASSWORD_USERNAME_BDD, __PROD_BDD)
    result = select_fields_with_where_equal_condition(
        cursor, ['core_size'], 'Compilations',
        {'cid': cid, 'incremental_mod': 0})
    if not len(result):
        raise ValueError("The cid {} doesn't exist in the "
                         "database or correspond to an incremental "
                         "compilation.".format(cid))
    return int(result[0][0])


def get_size_from_database_result(cid):
    cursor = fetch_cursor_to_database(
        __IP_BDD, __USERNAME_BDD, __PASSWORD_USERNAME_BDD, __RESULT_BDD)
    result = select_fields_with_where_equal_condition(
        cursor, ['compiled_kernel_size'], 'compilations',
        {'cid': cid})
    if not len(result):
        raise ValueError("The cid {} doesn't exist in the "
                         "database.".format(cid))
    return int(result[0][0])


def parser():
    parser = argparse.ArgumentParser(
        description=''  # TODO
    )
    parser.add_argument(
        "first_cid",
        type=int,
        help="The first cid to retrieve from the database."
    )
    parser.add_argument(
        "last_cid",
        type=int,
        help="The last cid retrieve from the database."
    )
    parser.add_argument(
        "--directory",
        help="The directory where the temporary file(s) will be stored.",
        default="."
    )
    return parser.parse_args()


def silent_remove(path):
    try:
        os.remove(path)
    except FileNotFoundError:
        pass


def clear_directory(path):
    for file in os.listdir(path):
        file_path = os.path.join(path, file)
        if os.path.isfile(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)


def retrieve_cid_prod(logs_path):
    for file in os.listdir(logs_path):
        file_path = os.path.join(logs_path, file)
        if os.path.isdir(file_path):
            return int(file)
    raise FileNotFoundError("Haven't found the cid_prd.")


if __name__ == '__main__':
    args = parser()

    logs_path = "{}/logs_{}".format(
        args.directory, str(time()).replace('.', ''))
    logs_path = os.path.abspath(logs_path)
    config_path = "{}/config_{}.config".format(
        args.directory, str(time()).replace('.', ''))
    config_path = os.path.abspath(config_path)
    script_path = os.path.dirname(os.path.realpath(__file__))
    os.makedirs(logs_path)

    for cid_prod in range(args.first_cid, args.last_cid+1):
        try:
            config = get_config_from_database_prod(cid_prod)
        except ValueError:
            continue

        with open(config_path, 'w') as config_file:
            config_file.write(config)
            config_file.flush()

        cmd_compiler = "{}/../kernel_generator.py 1 --dev --local --logs {} " \
                       "--config {}".format(script_path, logs_path, config_path)
        subprocess.run(
            args=cmd_compiler,
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )

        cid_result = retrieve_cid_prod(logs_path)
        print("{} {} {}".format(
            cid_prod,
            cid_result,
            get_size_from_database_prod(cid_prod) ==
            get_size_from_database_result(cid_result)
        ))
        clear_directory(logs_path)

    silent_remove(config_path)
    shutil.rmtree(logs_path)
