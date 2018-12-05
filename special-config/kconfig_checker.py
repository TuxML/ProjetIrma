import os
import subprocess
from pathlib import Path
import re

def get_linux_kernel(name, path=None):
    if path is not None:
        os.chdir(path)
    name += ".tar.xz"
    list_dir = os.listdir('.')
    if name not in list_dir:
        print("Linux kernel not found, downloading...")
        wget_cmd = "wget https://cdn.kernel.org/pub/linux/kernel/v4.x/{}".format(name)
        subprocess.call(wget_cmd, shell=True)
        extract_cmd = "tar -xf {}".format(name)
        subprocess.call(extract_cmd, shell=True)
    else:
        print("Linux kernel found.")


def generate_n_config(n, file):
    max = n
    if Path(file).is_file():
        cmd = "make KCONFIG_ALLCONFIG=" + file + " randconfig"
        while n:
            status = subprocess.call(cmd, shell=True)
            if status:
                print("Error while calling " + cmd + " aborting")
                exit(-1)
            store_config_file(n, max)
            n = n - 1
    check(max, file)


def store_config_file(n, max):
    config_n = "config" + str((max - n))
    path = "gen_config/"
    destination = path + config_n
    os.rename(".config", config_n)
    os.rename(config_n, destination)


def check(n, file):
    max = n
    nb_err = 0
    os.chdir("gen_config")
    with open(file) as fd:
        fd_str = (ln.strip() for ln in fd)
        print(fd_str)
        while n:
            for word in fd_str:
                if word not in open("config"+str(max-n)).read():
                    nb_err += 1
            display_error(max-n, nb_err)
            n -= 1


def display_error(nb_config_file, nb_error):
    if nb_error:
        print("there is {} error in file .config{}\n".format(nb_error, nb_config_file))
    else:
        print("No error in file .config{}\n".format(nb_config_file))



if __name__ == '__main__':
    get_linux_kernel("linux-4.13.3")
    os.chdir("linux-4.13.3")
    try:
        os.mkdir("gen_config")
    except Exception as e:
        print(e)
    generate_n_config(2, "../core/tuxml.config")
    print("end")

