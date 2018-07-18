#!/usr/bin/env python2.7

import argparse
import subprocess


def run():
    null = subprocess.call("oarsub -S ./spring.sh", shell=True)
    if null == -1:
        print("Error during the call of 'spring.sh'")


def setting(args):
    with open("params.txt", "w") as file:
        for i in range(args.Number_of_machines):
            file.write(str(args.Number_of_compilations) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("Number_of_compilations", type=int,
                        help="Number of compilations to do", nargs='?', default=1)
    parser.add_argument("Number_of_machines", type=int,
                        help="Number of Machines to use", nargs='?', default=1)
    args = parser.parse_args()

    print(" | ".join([k + ' : ' + str(vars(args)[k]) for k in vars(args)]))

    setting(args)

    run()


if __name__ == '__main__':
    main()
