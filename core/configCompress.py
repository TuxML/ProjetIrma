#!/usr/bin/python3

import argparse
import tuxml_settings as set

## @file configCompress.py
# @author LE MASLE Alexis
# @author POLES Malo
# @copyright Apache License 2.0
# @brief Recompile with different kernel compressions
#
# @details Running this script is only to rewrite .config with a different compression set up
# you need to choose between different compressions methods then it will be enable in the .config file
# the second effect is to disable other compressions that could be enable. If GZIP was enable and
# you choose BZIP2, then GZIP will be disable and commented, BZIP2 will be set at "y".
# It take place in the "harvesting data" part to gather different size about kernel compressions.

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


## rewrite a line in .config file
# @author POLES Malo
# @version 1
# @brief find an old line and rewrite it with a new line in .config file
# @param old Old line to find, can be partial match first occurrence
# @param new New line to write
# @param path_to_config Path to the file '.config' should not include '.config'
def rewrite(old, new, path_to_config):
    try:
        with open(path_to_config+".config", "r+") as f:
            nb_line = f.read().find(old)
            if nb_line == -1:  # sometimes there is no match because the options is already set as this value
                return
            f.seek(nb_line)
            f.write(new+"\n")
            f.close()
    except IOError as err:
        print("{}".format(err))
        exit(-1)


## choose the compression to enable
# @author POLES Malo
# @version 1
# @brief Choose the compression type to enable in .config file disable all the others ones
# @param Compress Type of compression as string
# @param path_to_config Path to the file '.config' should not include '.config'
def enable(compress, path_to_config):

    compression = set.COMPRESS_TYPE
    # enable
    rewrite("# CONFIG_KERNEL_" + compress + " is not set",
            "CONFIG_KERNEL_" + compress + "=y", path_to_config)
    # disable
    for c in compression:
            if not c == compress:
                rewrite("CONFIG_KERNEL_" + c + "=y",
                        "# CONFIG_KERNEL_" + c + " is not set", path_to_config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("compression", type=str, choices=set.COMPRESS_TYPE,
                        help="Precise the compression you wish to use in the .config file")
    parser.add_argument("path", type=str, help="Path to the .config file to change")
    args = parser.parse_args()
    enable(args.compression, args.path)
