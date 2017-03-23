#!/usr/bin/env python
#
# Copyright (c), 2015-2016, Quantum Espresso Foundation and SISSA (Scuola
# Internazionale Superiore di Studi Avanzati). All rights reserved.
# This file is distributed under the terms of the MIT License. See the
# file 'LICENSE' in the root directory of the present distribution, or
# http://opensource.org/licenses/MIT.
# Authors: Davide Brunato, Giovanni Borghi
#
"""
Convert from XML input  to Fortran input
"""

import sys


def parse_args():
    """Command arguments parsing"""
    import argparse

    parser = argparse.ArgumentParser(
            description="This program converts an XML input to the an equivalent "
                        "input file written in a format that is natively readable "
                        "by Fortran's codes of Quantum Espresso"
    )
    parser.add_argument("-v", "--verbosity", action="count", default=1,
                        help="Increase output verbosity.")
    parser.add_argument('-in', required=True, help="XML input filename.")
    return parser.parse_args()


if __name__ == '__main__':

    # Python 2.7+ is required. For old versions 'argparse' is available
    # only with extra package: https://pypi.python.org/pypi/argparse.
    if sys.version_info < (2, 7, 0):
        sys.stderr.write("You need python 2.7 or later to run this program\n")
        sys.exit(1)

    args = parse_args()
    print(args)

    if __package__ is None:
        from os import path
        sys.path.append(path.dirname(path.dirname(path.dirname(path.abspath(__file__)))))

    import qespresso
    import os

    qespresso.set_logger(args.verbosity)

    xml_conf = None
    input_fn = getattr(args, 'in')
    with open(input_fn) as input_fh:
        for line in input_fh:
            if '<neb:nebRun' in line:
                xml_conf = qespresso.NebDocument()
                break
            elif '<qes:espresso' in line:
                xml_conf = qespresso.PwDocument()
                break

    if xml_conf is None:
        sys.stderr.write("Could not find correct XML in %s, exiting...\n"
                         % input_fn)
        sys.exit(1)

    xml_conf.read(input_fn)
    pw_in = xml_conf.get_qe_input()

    input_fn_name, input_fn_ext = os.path.splitext(input_fn)
    outfile = input_fn_name + '.in'

    with open(outfile, mode='w') as f:
        f.write(pw_in)
        print("Input configuration written to file '%s' ..." % outfile)
