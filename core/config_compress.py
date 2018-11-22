#!/usr/bin/python3

import argparse
import tuxml_settings as set

## @file config_compress.py
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
# @param path_to_config Path to the file '.config' (should not contain a slash, and shoud not include '.config')
# TODO: something can go wring at several places and we always return True (of course we should handle exceptions)
def rewrite(old, new, path_to_config):
    # we read all lines
    f = open(path_to_config + "/.config", "r")
    lines = f.readlines()
    f.close()

    # and then replace old by new (TODO: regular expression)
    # we replace the content of config file (ie we write the new content into the same config file)
    for line in lines:
        if line == old + "\n":
            lines[lines.index(line)] = new + '\n'

            f = open(path_to_config + "/.config", "w")
            f.seek(0)
            f.writelines(lines)
            f.close()

    return True



## choose the compression to enable
# @author POLES Malo
# @version 1
# @brief Choose the compression type to enable in .config file disable all the others ones
# @param Compress Type of compression as string
# @param path_to_config Path to the file '.config' should not include '.config'
def enable(compress, path_to_config):

    compression = set.COMPRESS_TYPE # set of all compression methods

    # enable
    activating = rewrite("# CONFIG_KERNEL_" + compress + " is not set", "CONFIG_KERNEL_" + compress + "=y", path_to_config)
    if (not activating):
        print("Unable to activate compression option", str(compress), flush=True)
        return -1
        
    # disable
    for c in compression:
            if not c == compress:
                if not rewrite("CONFIG_KERNEL_" + c + "=y", "# CONFIG_KERNEL_" + c + " is not set", path_to_config):
                    print ("Unable to deactivate compression option", str(compress), flush=True)
                    return -1
    
    return 1

# TODO: unnecessary
# TODO: rather unit tests
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("compression", type=str, choices=set.COMPRESS_TYPE,
                        help="Precise the compression you wish to use in the .config file")
    parser.add_argument("path", type=str, help="Path to the .config file to change")
    args = parser.parse_args()
    enable(args.compression, args.path)
