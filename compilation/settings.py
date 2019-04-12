TUXML_VERSION = "v2.0"

IP_BDD = "148.60.11.195"
USERNAME_BDD = "script2"
PASSWORD_USERNAME_BDD = "ud6cw3xNRKnrOz6H"
NAME_BDD = "IrmaDB_result"

LOG_DIRECTORY = "/TuxML/logs"
OUTPUT_FILE = "{}/user_output.log".format(LOG_DIRECTORY)
STDOUT_FILE = "{}/stdout.log".format(LOG_DIRECTORY)
STDERR_FILE = "{}/stderr.log".format(LOG_DIRECTORY)
BOOT_FILE = "{}/boot.log".format(LOG_DIRECTORY)

TINY_CONFIG_SEED_FILE = "/TuxML/compilation/x64.config"
CONFIG_SEED_FILE = "/TuxML/compilation/tuxml.config"

DEPENDENCIES_FILE = "/dependencies.txt"
KERNEL_VERSION_FILE = "/kernel_version.txt"

KERNEL_COMPRESSION_TYPE = ["GZIP", "BZIP2", "LZMA", "XZ", "LZO", "LZ4"]
KERNEL_COMPRESSION_EXTENSIONS = [".gz", ".bz2", ".lzma", ".xz", ".lzo", ".lz4"]

BOOTING_KERNEL_PATH = "{}/arch/x86/boot/bzImage"
INITRAMFS_PATH = "/root/kdev/build/initramfs-busybox-x86.cpio.gz"
MAX_TIME_BOOT = 300
