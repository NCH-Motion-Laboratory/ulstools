# -*- coding: utf-8 -*-
"""
environment utilities

@author: Jussi (jnu@iki.fi)
"""

import psutil
import os
import logging
from pathlib import Path

import win32com.client


logger = logging.getLogger(__name__)


def make_shortcut(script_prefix, title=None):
    """Create a desktop shortcut that runs a script in the currently active
    conda environment. Designed to work with setuptools console_scripts
    entry points. Windows only.""" 
    
    # home = Path.home()  # Py3 pathtools only
    home = Path(os.path.expanduser('~'))
    desktop = home / 'Desktop'
    link_filename = ('%s.lnk' % (title or script_prefix))
    link_path = desktop / link_filename

    # for some reason CONDA_ROOT is not set, so get root from executable path
    anaconda_python = Path(os.environ['CONDA_PYTHON_EXE'])
    envdir = Path(os.environ['CONDA_PREFIX'])
    anaconda_root = anaconda_python.parent

    pythonw = anaconda_root / 'pythonw.exe'
    cwp = anaconda_root / 'cwp.py'
    pythonw_env = envdir / 'pythonw.exe'
    script = envdir / 'Scripts' / ('%s-script.py' % script_prefix)

    if not script.is_file():
        raise FileNotFoundError('cannot find script file at %s' % script)

    args = '%s %s %s %s' % (cwp, envdir, pythonw_env, script)

    shell = win32com.client.Dispatch("WScript.Shell")
    shortcut = shell.CreateShortCut(str(link_path))
    shortcut.Targetpath = str(pythonw)
    shortcut.arguments = args
    shortcut.save()


def already_running(script_prefix):
    """Try to figure out if the script is already running"""
    script_name = '%s-script.py' % script_prefix
    nprocs = 0
    for proc in psutil.process_iter():
        try:
            cmdline = proc.cmdline()
            if cmdline:
                if 'python' in cmdline[0] and len(cmdline) > 1:
                    if script_name in cmdline[1]:
                        logging.debug('found running process %s' % cmdline[1])
                        nprocs += 1
                        if nprocs == 2:
                            return True
        # catch NoSuchProcess for procs that disappear inside loop
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    return False




