import os
import subprocess
import re
import errno 
import pandas as pd 

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
    if os.path.isfile(file):
        cmd = "KCONFIG_ALLCONFIG=" + file +  " make randconfig"
        print("compilation command", cmd, "in", os.getcwd())
        while n:
            status = subprocess.call(cmd, shell=True)
            if status:
                print("Error while calling " + cmd + " aborting")
                exit(-1)
            store_config_file(n, max)
            n = n - 1
    else:
        print(file, "does not exist")
    


def store_config_file(n, max):
    config_n = "config" + str((max - n))
    path = "gen_config/"
    destination = path + config_n
    os.rename(".config", config_n)
    os.rename(config_n, destination)


def check(n, file):
    max = n
    report_data = pd.DataFrame(columns=['configid', 'nberrors', 'options'])
    with open(file) as fd:
        os.chdir("gen_config")
        # AM: don't get it, I removed it
        fd_str = [ln.strip() for ln in fd]
        print("pre-set options to check", fd_str)       
        
        while n:
            nb_err = 0
            diff_options =  []
            for opt in fd_str:
                # opt is in the form CONFIG_XXX=y
                s = opt.split('=')
                opt_name = s[0] # option name
                opt_value = s[1] # y, n, or m
                content_config = open("config"+str(max-n)).read()
                # we verify that the option is not set to yes
                if opt_value == 'n':
                    # TODO: check that comment 'CONFIG_XXX  is not set' appears? 
                    opt_yes = opt_name + "=" + "y"
                    opt_m = opt_name + "=" + "m"
                    if opt_yes in content_config and opt_m in content_config:
                        #print(opt, "should be 'n' but is 'y' or 'm")
                        diff_options.append(opt)
                        nb_err += 1
                elif opt_value == 'y':
                    if opt not in content_config:
                        #print(opt, "should be 'y' but is 'n' or 'm")
                        diff_options.append(opt)
                        nb_err += 1
                else:
                    print("TODO (module?)")
            #display_error(max-n, nb_err)
            report_data.loc[n] = (n, nb_err, diff_options)
            n -= 1
    return report_data

def display_error(nb_config_file, nb_error):
    if nb_error > 0:
        print("there is {} error in file config{}\n".format(nb_error, nb_config_file))
    else:
        print("No error in file config{}\n".format(nb_config_file))


def generate_and_check(nrep, file_spe_options):
    generate_n_config(nrep, file_spe_options)
    return check(nrep, file_spe_options)


if __name__ == '__main__':
    get_linux_kernel("linux-4.13.3")
    os.chdir("linux-4.13.3")
    try:
        os.mkdir("gen_config")
    except OSError as exc:  
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise
    nrep=1000
    file_spe_options="../core/tuxml.config"
    #print(generate_and_check(nrep, file_spe_options))
    # if you only want to check, simply call check (see below)
    rep = check(nrep, file_spe_options)
    # print(rep)
    uniq_opts = []
    for opt in rep['options']:
        if opt not in uniq_opts:
            uniq_opts.append(opt)        
    print(uniq_opts)
    nerrors = rep['nberrors'].sum()
    print((nerrors / len(rep)))

