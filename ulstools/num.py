# -*- coding: utf-8 -*-
"""
Miscellaneous numerical utilities.

@author: Jussi (jnu@iki.fi)
"""

import datetime


def check_hetu(hetu):
    """Check validity of a Finnish social security number (hetu).

    Last character of Finnish SSNs is a simple checksum, calculated from rest of
    the SSN. This allows detection of whether the SSN is correct.

    Parameters
    ----------
    hetu : str
        The SSN.

    Returns
    -------
    bool
        True if the input is a valid Finnish SSN, False otherwise.
    """
    if len(hetu) != 11 or hetu[6] not in '+-A':
        return False
    try:
        datetime.datetime.strptime(hetu[:6], '%d%m%y')
    except ValueError:
        return False
    # check 'checksum'
    chrs = "0123456789ABCDEFHJKLMNPRSTUVWXY"
    chk = chrs[(int(hetu[:6] + hetu[7:10])) % 31]
    if hetu[-1] != chk:
        return False
    return True


def age_from_hetu(hetu, d1=None):
    """Return age (in years) based on hetu (Finnish SSN).

    Parameters
    ----------
    hetu : str
        The SSN.
    d1 : datetime.date, optional
        If given, return age at date d1. Otherwise, return age at current
        system time.

    Returns
    -------
    age : int
        Age in years.

    """
    if not hetu:
        return None
    if not check_hetu(hetu):
        raise ValueError('Invalid hetu')
    if d1 is None:
        d1 = datetime.date.today()
    day, month, yr = int(hetu[:2]), int(hetu[2:4]), int(hetu[4:6])
    yr += {'+': 1800, '-': 1900, 'A': 2000}[hetu[6]]
    d0 = datetime.date(yr, month, day)
    return d1.year - d0.year - ((d1.month, d1.day) < (d0.month, d0.day))
