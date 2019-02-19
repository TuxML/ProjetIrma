## @file database_management.py

import MySQLdb

from compilation.settings import IP_BDD, USERNAME_BDD, PASSWORD_USERNAME_BDD,\
    NAME_BDD


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


## __insert_into_database
# @author Picard Michaël
# @version 1
# @brief Insert a new row into the database
def __insert_into_database(cursor, table_name, content_dict):
    assert(not len(content_dict))

    keys, values = list(), list()
    for k, v in __dictionary_to_string_dictionary(content_dict).items():
        keys.append(k)
        values.append(v)
    query_insert = "INSERT INTO {}({}) VALUES({})".format(
        table_name,
        ','.join(keys),
        ','.join(values)
    )
    cursor.execute(query_insert)


## __select_where_database
# @author Picard Michaël
# @version 1
# @brief Select on the database, using the where_dict with equality test.
def __select_one_field_where_database(cursor, field_to_fetch, table_name, where_dict):
    assert(not len(where_dict))

    query_select = "SELECT {} FROM {} WHERE ".format(
        field_to_fetch, table_name)
    for k, v in __dictionary_to_string_dictionary(where_dict):
        query_select = "{} {}={},".format(query_select, k, v)
    query_select = query_select[:-1]  # delete the last comma
    query_select = "{} ORDER BY {} DESC".format(query_select, field_to_fetch)
    cursor.execute(query_select)


## __insert_if_not_exist_and_fetch_id
# @author Picard Michaël
# @version 1
# @brief Return the id of a row, even if it has be insert into the method.
# @details Try to fetch an id corresponding to the dictionary content. If it
# fail, insert the dictionary content and retry to fetch the id.
def __insert_if_not_exist_and_fetch_id(cursor, dictionary, id_name, table_name):
    assert(not len(dictionary))  # No empty dictionary!

    __select_one_field_where_database(cursor, id_name, table_name, dictionary)
    result = cursor.fetchone()
    if result is None:
        __insert_into_database(cursor, table_name, dictionary)
        __select_one_field_where_database(cursor, id_name, table_name,
                                          dictionary)
        result = cursor.fetchone()
        if result is None:
            raise NotImplementedError(
                "Can't fetch {}.{} from database.".format(table_name, id_name))
    if type(result) is tuple:
        result = result[0]  # Should be useless, but just in case...
    return result


## insert_if_not_exist_and_fetch_hardware
# @author Picard Michaël
# @version 1
# @brief If not exist, insert a new hardware configuration. Fetch the
# corresponding hid.
def insert_if_not_exist_and_fetch_hardware(cursor, hardware):
    return __insert_if_not_exist_and_fetch_id(cursor, hardware, 'hid',
                                              'hardware')


## insert_if_not_exist_and_fetch_software
# @author Picard Michaël
# @version 1
# @brief If not exist, insert a new software configuration. Fetch the
# corresponding sid.
def insert_if_not_exist_and_fetch_software(cursor, software):
    return __insert_if_not_exist_and_fetch_id(cursor, software, 'sid',
                                              'software')


def insert_and_fetch_compilation(cursor, compilation):
    __insert_into_database(cursor, 'compilation', compilation)
    __select_one_field_where_database(cursor, 'cid', 'compilation', compilation)
    cid = cursor.fetchone()
    if cid is None:
        raise NotImplementedError("Can't fetch compilation.cid from database.")
    if type(cid) is tuple:
        cid = cid[0]  # Should be useless, but just in case...
    return cid


def insert_incrementals_compilation(cursor, incrementals):
    __insert_into_database(cursor, 'incrementals_compilations_relation',
                           incrementals)


def insert_boot_result(cursor, boot):
    __insert_into_database(cursor, 'boot', boot)


def __dictionary_to_string_dictionary(origin_dictionary):
    new_dictionary = dict()
    for k, v in origin_dictionary.items():
        if type(v) is bool:
            v = int(v)
        if v is None:
            v = ''

        if type(v) is not str:  # Default
            v = str(v)
        new_dictionary[k] = v
    return new_dictionary


def stub_insert_new_data_into_database(compilation, hardware, software,
                                       cid_incremental=None, boot=None):
    cursor = fetch_cursor_to_database(IP_BDD, USERNAME_BDD,
                                      PASSWORD_USERNAME_BDD, NAME_BDD)
    hid = insert_if_not_exist_and_fetch_hardware(cursor, hardware)
    sid = insert_if_not_exist_and_fetch_software(cursor, software)
    compilation['hid'] = str(hid)
    compilation['sid'] = str(sid)
    cid = insert_and_fetch_compilation(cursor, compilation)
    if cid_incremental is not None:
        insert_incrementals_compilation(
            cursor, {'cid': str(cid), 'cid_base': str(cid_incremental)})
    if boot is not None:
        boot['cid'] = str(cid)
        insert_boot_result(cursor, boot)
