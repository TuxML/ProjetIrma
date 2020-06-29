## @file database_management.py

import MySQLdb


## fetch_connection_to_database
# @author PICARD Michaël
# @version 1
# @brief Connect yourself to your database, and return a connection on it.
def fetch_connection_to_database(host, user, password, database_name):
    return MySQLdb.connect(
        host=host,
        user=user,
        passwd=password,
        db=database_name
    )


## __insert_into_database
# @author PICARD Michaël
# @version 1
# @brief Insert a new row into the database
def __insert_into_database(connection, cursor, table_name, content_dict):
    assert(len(content_dict))

    keys, values = list(), list()
    for k, v in content_dict.items():
        keys.append(k)
        values.append(v)
    query_insert = "INSERT INTO {}({}) VALUES({})".format(
        table_name,
        ','.join(keys),
        ','.join(["%s"] * len(values))
    )
    cursor.execute(query_insert, values)
    connection.commit()


## __select_where_database
# @author PICARD Michaël
# @version 1
# @brief Select on the database, using the where_dict with equality test.
def __select_one_field_where_database(cursor, field_to_fetch, table_name, where_dict):
    assert(len(where_dict))

    value = list()
    query_select = "SELECT {} FROM {} WHERE".format(
        field_to_fetch, table_name)
    for k, v in where_dict.items():
        query_select = "{} {}=%s and".format(query_select, k)
        value.append(v)
    query_select = query_select[:-4]  # delete the last and
    query_select = "{} ORDER BY {} DESC".format(query_select, field_to_fetch)
    cursor.execute(query_select, value)


## __insert_if_not_exist_and_fetch_id
# @author PICARD Michaël
# @version 1
# @brief Return the id of a row, even if it has be insert into the method.
# @details Try to fetch an id corresponding to the dictionary content. If it
# fail, insert the dictionary content and retry to fetch the id.
def __insert_if_not_exist_and_fetch_id(connection, cursor, dictionary, id_name, table_name):
    assert(len(dictionary))  # No empty dictionary!

    __select_one_field_where_database(cursor, id_name, table_name, dictionary)
    result = cursor.fetchone()
    if result is None:
        __insert_into_database(connection, cursor, table_name, dictionary)
        result = cursor.lastrowid
        if result is None:
            raise NotImplementedError(
                "Can't fetch {}.{} from database.".format(table_name, id_name))
    if type(result) is tuple:
        result = result[0]  # Should be useless, but just in case...
    return result


## insert_if_not_exist_and_fetch_hardware
# @author PICARD Michaël
# @version 1
# @brief If not exist, insert a new hardware configuration. Fetch the
# corresponding hid.
def insert_if_not_exist_and_fetch_hardware(connection, cursor, hardware):
    return __insert_if_not_exist_and_fetch_id(connection, cursor, hardware, 'hid',
                                              'hardware_environment')


## insert_if_not_exist_and_fetch_software
# @author PICARD Michaël
# @version 1
# @brief If not exist, insert a new software configuration. Fetch the
# corresponding sid.
def insert_if_not_exist_and_fetch_software(connection, cursor, software):
    return __insert_if_not_exist_and_fetch_id(connection, cursor, software, 'sid',
                                              'software_environment')


## insert_and_fetch_compilation
# @author PICARD Michaël
# @version 1
# @brief Insert new compilation result. Fetch the corresponding cid.
def insert_and_fetch_compilation(connection, cursor, compilation):
    __insert_into_database(connection, cursor, 'compilations', compilation)
    cid = cursor.lastrowid
    if cid is None:
        raise NotImplementedError("Can't fetch compilations.cid from database.")
    if type(cid) is tuple:
        cid = cid[0]  # Should be useless, but just in case...
    return cid


## insert_and_fetch_compilation
# @author PICARD Michaël
# @version 1
# @brief Insert new relation between two compilation (incrementals_compilation).
def insert_incrementals_compilation(connection, cursor, incrementals):
    __insert_into_database(connection, cursor, 'incrementals_compilations_relation',
                           incrementals)


## insert_and_fetch_compilation
# @author PICARD Michaël
# @version 1
# @brief Insert new boot result.
def insert_boot_result(connection, cursor, boot):
    __insert_into_database(connection, cursor, 'boot', boot)

## insert_sizes
# @author SAFFRAY Paul
# @version 1
# @brief Insert additional size results.
def insert_sizes(connection, cursor, sizes):
    __insert_into_database(connection, cursor, 'sizes', sizes)
