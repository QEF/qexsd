#
# Copyright (c), 2015-2019, Quantum Espresso Foundation and SISSA (Scuola
# Internazionale Superiore di Studi Avanzati). All rights reserved.
# This file is distributed under the terms of the MIT License. See the
# file 'LICENSE' in the root directory of the present distribution, or
# http://opensource.org/licenses/MIT.
#
# Authors: Davide Brunato
#
import logging
from collections.abc import MutableMapping

logger = logging.getLogger('qeschema')


def set_logger(loglevel=1, logfile=None):
    """
    Setup a basic logger with an handler and a formatter, using a
    corresponding numerical range [0..4], where a higher value means
    a more verbose logging. The loglevel value is mapped to correspondent
    logging module's value:

    LOG_CRIT=0 (syslog.h value is 2) ==> logging.CRITICAL
    LOG_ERR=1 (syslog.h value is 3) ==> logging.ERROR
    LOG_WARNING=2 (syslog.h value is 4) ==> logging.WARNING
    LOG_INFO=3 (syslog.h value is 6) ==> logging.INFO
    LOG_DEBUG=4 (syslog.h value is 7) ==> logging.DEBUG

    If a logfile name is passed then writes logs to file, instead of
    send logs to the standard output.

    :param loglevel: Simplified POSIX's syslog like logging level index
    :param logfile: Logfile name for non-scripts runs
    """
    global logger

    # Higher or lesser argument values are also mapped to DEBUG or CRITICAL
    effective_level = max(logging.DEBUG, logging.CRITICAL - loglevel * 10)

    logger.setLevel(effective_level)

    # Add the first new handler
    if not logger.handlers:
        if logfile is None:
            lh = logging.StreamHandler()
        else:
            lh = logging.FileHandler(logfile)
        lh.setLevel(effective_level)

        if effective_level <= logging.DEBUG:
            formatter = logging.Formatter("[%(levelname)s:%(module)s:%(funcName)s: %(lineno)s] %(message)s")
        elif effective_level <= logging.INFO:
            formatter = logging.Formatter("[%(levelname)s:%(module)s] %(message)s")
        else:
            formatter = logging.Formatter("%(levelname)s: %(message)s")

        lh.setFormatter(formatter)
        logger.addHandler(lh)
    else:
        for handler in logger.handlers:
            handler.setLevel(effective_level)


def etree_iter_path(elem, tag=None, path='.'):
    """
    Iterate an ElementTree structure giving back couples with an element and its path.

    :param elem: root of the ElementTree
    :param tag: Optional tag matching argument.
    :param path: Argument element path
    """
    if tag == "*":
        tag = None
    if tag is None or elem.tag == tag:
        yield elem, path
    for child in elem:
        child_path = '%s/%s' % (path, child.tag)
        for e, p in etree_iter_path(child, tag, path=child_path):
            yield e, p


def to_fortran(value):
    """
    Translate a Python value to the equivalent literal representation for Fortran input.
    Leading and trailing spaces characters are removed from strings.
    """
    if isinstance(value, bool):
        return '.true.' if value else '.false.'
    elif isinstance(value, str):
        return repr(value.strip())
    elif isinstance(value, bytes):
        return repr(value.decode('utf-8').strip())
    return str(value)


class BiunivocalMap(MutableMapping):
    """
    A dictionary that implements a bijective correspondence, namely with constraints
    of uniqueness both on keys and on values. Both keys and values must be hashable.
    """
    def __init__(self, *args, **kwargs):
        self.__map = {}
        self.__inverse = {}
        self.update(*args, **kwargs)

    def __getitem__(self, key):
        try:
            return self.__map[key]
        except KeyError:
            if not hasattr(self, '__missing__'):
                raise
            return getattr(self, '__missing__')(key)

    def __setitem__(self, key, item):
        try:
            if self.__inverse[item] != key:
                raise ValueError("Value '{0}' is already mapped by another key!".format(item))
        except KeyError:
            if key in self.__map:
                del self.__inverse[self.__map[key]]
            self.__map[key] = item
            self.__inverse[item] = key
        else:
            del self.__inverse[self.__map[key]]
            self.__map[key] = item
            self.__inverse[item] = key

    def __delitem__(self, key):
        del self.__inverse[self.__map[key]]
        del self.__map[key]

    def __iter__(self):
        return iter(self.__map)

    def __len__(self):
        return len(self.__map)

    def __contains__(self, key):
        return key in self.__map

    def __repr__(self):
        return '%s(%s)' % (self.__class__.__name__, self.__map or '')

    def copy(self):
        return self.__class__(self.__map.copy())

    def inverse(self):
        """Returns a copy of the inverse dictionary."""
        return self.__inverse.copy()

    def getkey(self, value, default=None):
        """
        If *value* is in dictionary's values, returns the key correspondent to the value,
        else returns the *default* argument.
        """
        try:
            return self.__inverse[value]
        except KeyError:
            return default
