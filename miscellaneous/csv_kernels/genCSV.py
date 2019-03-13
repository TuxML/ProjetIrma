#!/usr/bin/env python3
## @file genCSVlib.py
# @author Pierre Le Luron, Alexis LE MASLE
# @copyright Apache License 2.0
# @brief Base functions for CSV generation
# @details Functions necessary for CSV generation from a TuxML database to feed the ML on

import MySQLdb
import bz2
import sys
from sys import exit
import DBCredentials
import argparse

default_values = {
    "UNKNOWN": "0",
    "INT": "0",
    "HEX": "0x0",
    "STRING": None,
    "TRISTATE": "n",
    "BOOL": "n",
    "FLOAT": "0.0"
}

## Check if a character is a whitespace for .config parsing
# @param c character to check
# @returns boolean indicating if c is whitespace


def isWhitespace(c):
    return c == ' ' or c == '\t' or c == '\n'

## Extracts .config data and populates a dict (property name without prefix "CONFIG_" as key)
# @param configdata .config data (raw or bzipped)
# @param bz2_enabled indicates whether the data is encoded with bz2
# @returns output dict
# @throws ValueError if the .config is malformed


def scanConfig(configdata, bz2_enabled):
    # Decode
    if bz2_enabled:
        config = bz2.decompress(configdata).decode('ascii')
    else:
        config = configdata
    props = {}
    cursor = 0
    s = len(config)
    state = 0
    # 0 -> seeking name, comment, or end of file
    # 1 -> skipping comment
    # 2 -> writing name
    # 3 -> writing value
    name = ""
    value = ""
    while cursor < s:
        c = config[cursor]
        if state == 0:
            # Seek comment
            if c == '#':
                state = 1
            # Seek name
            elif not isWhitespace(c):
                state = 2
                name = c
        elif state == 1:
            # Seek end of line
            if c == '\n':
                state = 0
        elif state == 2:
            # Continue name
            if c != '=':
                name += c
            # Seek value
            else:
                state = 3
                value = ""
        elif state == 3:
            # Continue value
            if c != '\n':
                value += c
            else:
                # Validate name + value
                # Remove quotes
                if value[0] == '"' and value[-1] == '"':
                    value = value[1:-1]
                # Set in dict and remove leading "CONFIG_" in name
                props[name[7:]] = value
                state = 0
        cursor += 1
    if state == 2:
        raise ValueError("Incomplete .config file : " + str(props))
    return props

## Pretty progress bar
# @param p progress in percents


def printProgress(p):
    if p > 100:
        p = 100
    if p < 0:
        p = 0
    end = ""
    if p == 100:
        end = "\n"
    progress = p/5
    print("\rProgression: [", end="", flush=True)
    for i in range(int(progress)):
        print("#", end="", flush=True)
    for i in range(int(progress), 20):
        print("-", end="", flush=True)
    print("] " + str(int(p)) + "%", end=end, flush=True)

## Generates CSV file
# @param cid The cid where is the .config file ( -1 for all )


def genCSV(cid, From: int=None, To: int=None, incremental=True):

    inc = " AND incremental_mod = 0" if incremental == False else ""

    where = "WHERE cid = " + str(cid) + inc

    if (type(From) is int) and (type(To) is int):

        if From > To:
            From, To = To, From

        if To == From+1:
            cid = From
            where = "WHERE cid = " + str(cid) + inc
        elif not From == To:
            cid = 0
            where = "WHERE cid >= " + str(From) + " AND cid < " + str(To) + inc
        else:
            cid = From
            where = "WHERE cid = " + str(cid) + inc
            print("You choose a range from", From, "to", str(To) +
                  ".", "That is to say: cid =", cid, flush=True)

    if cid == -1:
        where = "WHERE compilation_time > -1 ORDER BY cid LIMIT %s OFFSET %s" + inc

    for creds in DBCredentials.db:
        try:
            # Connect to DB
            print("Connecting to db {} at {}...".format(
                creds["creds"]["db"], creds["creds"]["host"]), end="", flush=True)
            conn = MySQLdb.connect(**creds["creds"])
            cursor = conn.cursor()

            # Batches of requests
            offset = 0
            step = 50

            # Requests
            get_prop = "SELECT name, type FROM Properties"
            query = ("SELECT cid, config_file FROM {} " +
                     where).format(creds["table"])
            count_rows = ("SELECT COUNT(*) FROM {} " +
                          where).format(creds["table"])
            # End condition
            end = False

            # Extract properties
            cursor.execute(get_prop)
            types_results = list(cursor.fetchall())
            if len(types_results) == 0:
                print("\nError : Properties not present in database - You need to run Kanalyser first (https://github.com/TuxML/Kanalyser)")
                continue

            # Order properties and populate default values
            # names = [""]*len(types_results)
            defaults = [0]*len(types_results)
            order = {}
            index = 0
            for (name, typ) in types_results:
                order[name] = index
                # names[index] = name
                defaults[index] = default_values[typ]
                index += 1
            # Get row count
            cursor.execute(count_rows)
            tmp = cursor.fetchone()
            row_count = tmp[0]

            if row_count == 0:
                print("\nError, number of lines is 0",
                      file=sys.stderr, flush=True)
                cursor.close()
                exit(0)

            print("Done\nFilling rows :")

            # Request batches
            while not end:
                printProgress(100*offset/row_count)
                # Get results
                if cid == -1:
                    cursor.execute(query, (step, offset))
                else:
                    cursor.execute(query)
                    end = True

                results = cursor.fetchall()
                # Check if end
                if len(results) == 0:
                    end = True
                    break

                val_list = {}
                # Enumerate results
                for num, (ci, config_file) in enumerate(results):
                    try:
                        # Parse .config
                        props = scanConfig(config_file, creds["bz2"])
                        # Load default values
                        values = list(defaults)
                        # Overwrite default values
                        for (k, v) in props.items():
                            values[order[k]] = v

                        val_list[num] = values
                    except ValueError as e:
                        # Bad .config
                        pass

                # end
                if not cid == -1 and cid == 0:
                    cursor.close()
                    printProgress(100)
                    assert type(
                        val_list) is dict, "val_list is not a dict type"
                    return val_list

                offset += step

            # Its over
            cursor.close()
            printProgress(100)
            assert type(
                val_list) is dict, "val_list is not a dict type"
            return val_list

        except MySQLdb.Error as err:
            print("\nError : Can't read from db : {}".format(err.args[1]))
            continue
        finally:
            conn.close()


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("cid", type=int, help="The cid from database to fetch")
    parser.add_argument(
        "From", type=int, help="From the cid ( to use with \"To\")", nargs="?", default=None)
    parser.add_argument(
        "To", type=int, help="To the cid ( to use with \"From\")", nargs="?", default=None)
    args = parser.parse_args()

    if bool(args.To) != bool(args.From):
        print("To and From must been used together")
        exit(0)

    genCSV(args.cid, args.From, args.To)
