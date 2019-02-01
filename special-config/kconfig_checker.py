import os
import subprocess
import re
import errno 
import pandas as pd 
import tempfile

import unittest


DEBUG=False

'''
Authors: Malo Poles and Mathieu Acher 
'''

def get_linux_kernel(name, path=None):
    if path is not None:
        os.chdir(path)
    name += ".tar.xz"
    list_dir = os.listdir('.')
    if name not in list_dir:
        print("Linux kernel not found, downloading...")
        wget_cmd = "wget https://cdn.kernel.org/pub/linux/kernel/v4.x/{}".format(name)
        try:
            if not DEBUG:
                subprocess.call(wget_cmd, shell=True)
            else:
                subprocess.call(wget_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as err:
            print(err)
        extract_cmd = "tar -xvf {}".format(name)
        try:
            subprocess.call(extract_cmd, shell=True)
        except OSError as err:
            print(err)

    else:
        if DEBUG:
            print("Linux kernel found.")


def generate_n_config(n, file):
    max = n
    if os.path.isfile(file):
        cmd = "KCONFIG_ALLCONFIG=" + file + " make randconfig"
        if DEBUG:
            print("compilation command", cmd, "in", os.getcwd())
        while n:
            if not DEBUG:
                status = subprocess.call(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) 
            else:
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
    os.chdir("gen_config")
    with open(file) as fd:        
        fd_str = [ln.strip() for ln in fd] # collect lines 
    if DEBUG:
        print("pre-set options to check", fd_str)       
    
    while n:
        nb_err = 0
        diff_options =  []
        for opt in fd_str:
            # opt is in the form CONFIG_XXX=y
            s = opt.split('=')
            opt_name = s[0] # option name
            opt_value = s[1] # y, n, or m
            with open("config"+str(max-n)) as cf:
                content_config = cf.read()
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
                    print("TODO (module?)", opt)
            report_data.loc[n] = (n, nb_err, diff_options)
            n -= 1
    return report_data





def generate_and_check(nrep, file_spe_options):
    # clean existing configuration files in gen_config 
    generate_n_config(nrep, file_spe_options)
    return check(nrep, file_spe_options)


# kernel name: kernel version (dowloads if needs be)
# nrep: how many times we call randconfig
# conf_file: file for presetting options
def randconfig_withpreoptions_test(nrep, conf_file, kernel_name, expert_enable=0):
    get_linux_kernel(kernel_name)
    os.chdir(kernel_name)
    try:
        os.mkdir("gen_config")
    except OSError as exc:
        if exc.errno == errno.EEXIST:
            pass
        else:
            raise
    file_spe_options = conf_file
    if expert_enable:
        print("Test with CONFIG_EXPERT append at the end of the file")
        file_spe_options2 = tempfile.NamedTemporaryFile(suffix=".config").name
        with open(file_spe_options) as f:
            lines = f.readlines()
            with open(file_spe_options2, "w") as f1:
                f1.writelines(lines)
                f1.write('\n')
                f1.write('CONFIG_EXPERT=y')
        rep = generate_and_check(nrep, file_spe_options2)
    else:
        if DEBUG:
            print("(Information) CONFIG_EXPERT not at the end of the configuration file, might (should) be still there because of dependances (workaround)")
        rep = generate_and_check(nrep, file_spe_options)

    # pointless?
    uniq_opts = []
    for opt in rep['options']:
        if opt not in uniq_opts:
            uniq_opts.append(opt)
    if DEBUG:
        print("unique options", uniq_opts)

    if DEBUG:
        nerrors = rep['nberrors'].sum()
        print("Results on kernel {}".format(kernel_name))
        print((nerrors / len(rep)), " (ratio of options whose values differ from pre-settings)")
        print("# errors report\n\n")
        print(rep)
        print("######\n\n")
    os.chdir("../..")
    return rep


# kernel name: kernel version (dowloads if needs be)
# nrep: how many times we call randconfig
# opt: preset options
def minimal_randconfig_test(opt, nrep, kernel_name):
    conf_file = os.getcwd() + "/minimal.config"
    with open(conf_file, "w+") as conf_mini:
        conf_mini.write(opt)
        conf_mini.close()
    return randconfig_withpreoptions_test(nrep, conf_file, kernel_name)

## for testing multiple kernel use kernel_list file wich should contains the kernel + versions, one line at the time
## the kernel must be present on https://cdn.kernel.org/pub/linux/kernel/

## for minimal tests ( test with only one pre set option ) invoke minimal_test method
## pre-conf to generate & test 100 files

## no clean up method exist yet

class TestRandconfigSpeMethods(unittest.TestCase):

    # linux version used (and so Kconfig files/randconfig version used)    
    # number of times we call randconfig (we repeat the procedure to see if the random process selects sometimes option)    
    def assert_spe_success(self, spe_options, iter_randconfig=10, linux_version="linux-4.20.1"):
        rep = minimal_randconfig_test(spe_options, iter_randconfig, linux_version)
        self.assertEqual(rep['nberrors'].sum(), 0.0)

    # same as above   
    # more iterations by default to falsify the specialization 
    def assert_spe_fail(self, spe_options, iter_randconfig=20, linux_version="linux-4.20.1"):
        rep = minimal_randconfig_test(spe_options, iter_randconfig, linux_version)
        self.assertNotEqual(rep['nberrors'].sum(), 0.0)

    # OK, no dependencies! 
    # we expect CONFIG_CC_OPTIMIZE_FOR_SIZE to be included all time 
    def test_cc_optimize(self):
        self.assert_spe_success("CONFIG_CC_OPTIMIZE_FOR_SIZE=y")       

    # CONFIG_SLOB alone is not enough (see hereafter), you need to explicitly set the value of its dependency CONFIG_EXPERT
    # we can disagree with this design choice/assumption (ie forcing to be explicit about dependencies), but it's the real behavior of randconfig 
    def test_slob_with_dependency(self):
        self.assert_spe_success("CONFIG_EXPERT=y\nCONFIG_SLOB=y")

    # CONFIG_EXPERT alone 
    def test_configexpert(self):
        self.assert_spe_success("CONFIG_EXPERT=y")

     # CONFIG_SLOB alone: (unfortunately) dependencies explicitly needed
     # randconfig does not propagate for you and so SLOB may be 'n'
    def test_slob_without_dependency(self):
        self.assert_spe_fail("CONFIG_SLOB=y")

     # CONFIG_X86_NEED_RELOCS has no dependency and is a "blind" option: there is no prompt associated; it is simply a shortcut to 
     # RANDOMIZE_BASE || (X86_32 && RELOCATABLE) 
     # it is helpful to "propagate" a combination of other options 
     # randconfig seems not considering such "blind" options 
     # since it is pointless to "test" an option that is actually not selectable 
     # we can disagree with this design choice, but it's how Kconfig/randconfig works
     # so CONFIG_X86_NEED_RELOCS will be sometimes 'n' (despite our pre-setting)
    def test_blind_option(self):
        self.assert_spe_fail("CONFIG_X86_NEED_RELOCS=y")


    # ~0.72  (ratio of options whose values differ from pre-settings) # https://github.com/torvalds/linux/blob/v4.20/lib/Kconfig.kasan 
    # basic reason: there is an "if HAVE_ARCH_KASAN" (not a "depends", but a conditional)
    # but there are "surprises" below)
    def test_kasan_ifdependency(self):
        self.assert_spe_fail("CONFIG_KASAN=y", iter_randconfig=20)

    # minimal_randconfig_test("linux-4.13.3", 100, "CONFIG_HAVE_ARCH_KASAN=y\nCONFIG_KASAN=y")  
    # 1.54  (ratio of options whose values differ from pre-settings) (AM: we need to divide the ratio by 2 right?) 
    # hum... 
    def test_kasan_withifdependency(self):
        self.assert_spe_fail("CONFIG_HAVE_ARCH_KASAN=y\nCONFIG_KASAN=y", iter_randconfig=20)

    # basic reason is that HAVE_ARCH_KASAN is not necessarily set to 'y' https://github.com/torvalds/linux/blob/master/lib/Kconfig.kasan 
    # it seems a blind option (no prompt)
    def test_archkasan(self):
        self.assert_spe_fail("CONFIG_HAVE_ARCH_KASAN=y", iter_randconfig=20)
    ## another attempt
    def test_archkasan_withX86_64(self):
        self.assert_spe_fail("CONFIG_X86_64=y\nCONFIG_HAVE_ARCH_KASAN=y", iter_randconfig=20) 
   
    

    # minimal_randconfig_test("linux-4.13.3", 100, "CONFIG_USB_SERIAL_OPTICON=y") 
    # 0.89  (ratio of options whose values differ from pre-settings) 
    # https://github.com/torvalds/linux/blob/v4.20/drivers/usb/serial/Kconfig 
    # if USB_SERIAL
    def test_usb_opticon(self):
        self.assert_spe_fail("CONFIG_USB_SERIAL_OPTICON=y", iter_randconfig=20) 
    # with USB_SERIAL (dependency) and depends on CONFIG_TTY as well https://github.com/torvalds/linux/blob/v4.20/drivers/tty/Kconfig 
    # which itself depends on CONFIG_EXPERT 
    def test_usb_option_with_serial(self):
        self.assert_spe_success("CONFIG_EXPERT=y\nCONFIG_TTY=y\nCONFIG_USB_SERIAL=y\nCONFIG_USB_SERIAL_OPTICON=y", iter_randconfig=20) 
    

    

if __name__ == '__main__':

    ###  testing randconfig spe on different kernel versions of kernel_list
    #with open("kernel_list") as kl:
    #    kernels = [ln.strip() for ln in kl]
    #    kl.close()
    #for k in kernels:
    #    print("Testing randconfig with kernel", k)
    #    minimal_randconfig_test(k, 100, "CONFIG_SLOB=y")
        
    # other usage examples:
    # randconfig_withpreoptions_test("linux-4.13.3", 100, "../../core/tuxml.config")
    # minimal_randconfig_test("linux-4.13.3", 100, "CONFIG_SLOB=y") # dependencies explicitly needed, see below


    ##### TODO (Mathieu: I will fix the migration process to unit tests)
  
   # minimal_randconfig_test("linux-4.13.3", 100, "CONFIG_KASAN_OUTLINE=y") # depends on KASAN # 0.91  (ratio of options whose values differ from pre-settings)
    # minimal_randconfig_test("linux-4.13.3", 100, "CONFIG_DVB_USB=y\nCONFIG_DVB_USB_DIBUSB_MB=y") # 1.96  (ratio of options whose values differ from pre-settings) # https://github.com/torvalds/linux/blob/master/drivers/media/usb/dvb-usb/Kconfig
    # minimal_randconfig_test("linux-4.13.3", 100, "CONFIG_TTY=y\nCONFIGT_HCIUART=y") # 1.0  (ratio of options whose values differ from pre-settings) (should be divided by 2) # https://github.com/torvalds/linux/blob/master/drivers/bluetooth/Kconfig 
    # minimal_randconfig_test("linux-4.20.1", 100, "CONFIG_BT_QCOMSMD=y") # 0.89  (ratio of options whose values differ from pre-settings) # https://github.com/torvalds/linux/blob/master/drivers/bluetooth/Kconfig
    # minimal_randconfig_test("linux-4.20.1", 100, "CONFIG_BT=y\nCONFIG_BT_QCOMSMD=y") # 1.36  (ratio of options whose values differ from pre-settings) # BT seems needed (menu option) # https://github.com/torvalds/linux/blob/master/net/bluetooth/Kconfig
    # minimal_randconfig_test("linux-4.20.1", 10, "CONFIG_NET=y\nCONFIG_S390=n\nCONFIG_BT=y\nCONFIG_BT_QCOMSMD=y") # 0.9  (ratio of options whose values differ from pre-settings)
    # minimal_randconfig_test("linux-4.20.1", 100, "CONFIG_RFKILL=y\nCONFIG_NET=y\nCONFIG_S390=n\nCONFIG_BT=y\nCONFIG_BT_QCOMSMD=y") # with the infamous RFKILL || !RFKILL  # 0.53  (ratio of options whose values differ from pre-settings)
    # minimal_randconfig_test("linux-4.13.3", 100, "CONFIG_BT_QCOMSMD=n") # OK! 0.0  (ratio of options whose values differ from pre-settings)
    # minimal_randconfig_test("linux-4.20.1", 10, "CONFIG_ARM_EXYNOS_BUS_DEVFREQ=y") # 0.8  (ratio of options whose values differ from pre-settings)
    # minimal_randconfig_test("linux-4.20.1", 10, "CONFIG_PM_DEVFREQ=y\nCONFIG_ARM_EXYNOS_BUS_DEVFREQ=y") # 0.5  (ratio of options whose values differ from pre-settings) # depends on ARCH_EXYNOS || COMPILE_TEST # https://github.com/torvalds/linux/blob/master/drivers/devfreq/Kconfig
    # minimal_randconfig_test("linux-4.20.1", 100, "CONFIG_COMPILE_TEST=y\nCONFIG_PM_DEVFREQ=y\nCONFIG_ARM_EXYNOS_BUS_DEVFREQ=y") # 0.0 since we force # https://github.com/torvalds/linux/blob/master/drivers/devfreq/Kconfig
    # minimal_randconfig_test("linux-4.20.1", 100, "CONFIG_ARCH_EXYNOS=y\nCONFIG_PM_DEVFREQ=y\nCONFIG_ARM_EXYNOS_BUS_DEVFREQ=y")  # 1.58  (ratio of options whose values differ from pre-settings) # https://github.com/torvalds/linux/blob/v4.20/arch/arm64/Kconfig.platforms
    # minimal_randconfig_test("linux-4.20.1", 100, "CONFIG_ARCH_EXYNOS=y") # 1.0  (ratio of options whose values differ from pre-settings)
    # minimal_randconfig_test("linux-4.20.1", 100, "CONFIG_ARM64=y\nCONFIG_ARCH_EXYNOS=y") # 2.0  (ratio of options whose values differ from pre-settings)
    # minimal_randconfig_test("linux-4.20.1", 10, "CONFIG_ARM64=y") # 1.0  (ratio of options whose values differ from pre-settings)
    unittest.main()
    
    

    