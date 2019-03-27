#!/usr/bin/python3

## @file dependencies_tree_fixer
# @author PICARD Michaël
# @brief A simple python script to ensure that all the dependencies tree
# are correctly downloaded when building the compressed tuxml image.

import subprocess


def get_additional_dependencies():
    additional_dependencies = list()
    output = subprocess.check_output(
        args="apt-get install -s -y --no-install-recommends "
             "$(cat /dependencies.txt)",
        shell=True,
        universal_newlines=True
    ).splitlines()
    begin_additional_package_reading = False
    for line in output:
        if not begin_additional_package_reading and not line.startswith("The following additional packages will be installed:"):
            continue
        begin_additional_package_reading = True
        if line.startswith("The following additional packages will be installed:"):
            continue
        if line.startswith("Suggested packages:"):
            break
        additional_dependencies.extend(line.strip().split(" "))

    if len(additional_dependencies):
        print("Additional dependencies found.\n")

    return additional_dependencies


def add_additional_dependencies(dependencies = list()):
    assert(len(dependencies))
    dependencies = " ".join(dependencies)

    subprocess.run(
        args="apt-get install -qq -y --no-install-recommends "
             "--download-only {}".format(dependencies),
        shell=True
    )

    with open("./dependencies.txt", 'a') as file:
        file.write(dependencies)
        file.write('\n')
        file.flush()


if __name__ == "__main__":
    while True:
        dependencies_tree_list = get_additional_dependencies()
        if len(dependencies_tree_list):
            add_additional_dependencies(dependencies_tree_list)
        else:
            break
