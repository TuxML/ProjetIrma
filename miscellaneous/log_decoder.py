#!/usr/bin/env python3

import argparse
import bz2


def parser():
    parser = argparse.ArgumentParser(
        description=""  # TODO
    )
    parser.add_argument(
        "file",
        type=str,
        help="The path to file to decode."
    )
    parser.add_argument(
        "-o",
        "--output_name",
        type=str,
        help="The pathname to the decoded output file.",
        default="./output"
    )
    return parser.parse_args()


if __name__ == "__main__":
    args = parser()
    with open(args.file, "rb") as file_in:
        with open(args.output_name, "w") as file_out:
            file_out.write(bz2.decompress(file_in.read()).decode())
            file_out.flush()
