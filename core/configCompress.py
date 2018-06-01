#!/usr/bin/python3

import subprocess
import argparse

## @file configCompress.py
# @author LE MASLE Alexis
# @copyright Apache License 2.0
# @brief Recompile with differents kernel compressions
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


parser = argparse.ArgumentParser()
parser.add_argument("compression", type=str, choices= ["GZIP","BZIP2","LZMA","XZ","LZO","LZ4"], help="Precise the compression you wish to use in the .config file")
args = parser.parse_args()

def rewrite(old, new):
    f = open(".config", "r")
    lines = f.readlines()
    f.close()

    for line in lines:
        if line == old + "\n":
            lines[lines.index(line)] = new + '\n'

            f = open(".config", "w")
            f.seek(0)
            f.writelines(lines)
            f.close()
            return 0

    return -1

# enable a compression and disable the others
def enable(compress):

    compression = ["GZIP","BZIP2","LZMA","XZ","LZO","LZ4"]
    if compress not in compression:
        print(compress,"not in compression list")
        return -1

    # enable
    rewrite("# CONFIG_KERNEL_" + compress+ " is not set", "CONFIG_KERNEL_" + compress + "=y")

    # disable
    for c in compression:
            if not c == compress:
                rewrite("CONFIG_KERNEL_" + c + "=y", "# CONFIG_KERNEL_" + c + " is not set")

    return 0



# main
if __name__ == "__main__":
    enable(args.compression)

    print("")
    subprocess.run("cat .config | grep CONFIG_KERNEL", shell=True)
