#!/usr/bin/python3

import wget
import tarfile
import os
from pathlib import Path
import subprocess
import shutil

HOME = str(Path.home())
EXPERIMENT_DIR = "KERNEL_EXPERIMENTS"
EXPERIMENT_DIR_PATH = HOME + '/' + EXPERIMENT_DIR
CSV_FILE_PATH = EXPERIMENT_DIR_PATH + "/kernel_options.csv"
MAKEFILE_PATCH_PATH = EXPERIMENT_DIR_PATH + "/makefile.patch"

if __name__ == "__main__":

    exp_dir = Path(EXPERIMENT_DIR_PATH)
    
    if not exp_dir.is_dir():
        os.mkdir(EXPERIMENT_DIR_PATH)

    shutil.copy("makefile.patch", EXPERIMENT_DIR_PATH)

    os.chdir(EXPERIMENT_DIR_PATH)
    fichier = open(CSV_FILE_PATH, "w")
    fichier.write("Kernel_version,ARCH,nb_options\n")
    fichier.close()  # TODO: find another solution if possible

    for i in range(21):
        os.chdir(EXPERIMENT_DIR_PATH)
        kernel_string = "linux-4.{}.1".format(i)
        kernel_path = EXPERIMENT_DIR_PATH + '/' + kernel_string

        ker_dir = Path(kernel_path)
        
        if not ker_dir.is_dir():
            wget_string = "http://cdn.kernel.org/pub/linux/kernel/v4.x/{}.tar.xz".format(kernel_string)
            linux_tar = wget.download(wget_string)
            with tarfile.open(linux_tar) as f:
                f.extractall('.')
            os.remove(linux_tar)

    i = 0
    for i in range(21):
        os.chdir(EXPERIMENT_DIR_PATH)
        kernel_string = "linux-4.{}.1".format(i)
        kernel_path = EXPERIMENT_DIR_PATH + '/' + kernel_string

        kernel_path_arch = kernel_path + "/arch/"
        LIST_ARCH = next(os.walk(os.path.join(kernel_path_arch, '.')))[1]
        for j in range(len(LIST_ARCH)):
            fichier = open(CSV_FILE_PATH, "a")
            fichier.write("{},{},".format(kernel_string, LIST_ARCH[j]))
            fichier.close()  # TODO: find another solution if possible (we open and close too many times)
            # TODO: check if folder exists
            os.chdir(kernel_path)

            str_patch = "patch -p1 < ../makefile.patch"
            subprocess.call(str_patch, shell=True)  # TODO: check result

            str_make = "make ARCH=" + LIST_ARCH[j] + " scriptconfig SCRIPT=" + HOME + "/PycharmProjects/Kanalyzer2/count_options.py"
            subprocess.call(str_make, shell=True)  # TODO: check result

    # shutil.rmtree(kernel_path)
