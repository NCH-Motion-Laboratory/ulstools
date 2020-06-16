# -*- coding: utf-8 -*-
"""
environment utilities

@author: Jussi (jnu@iki.fi)
"""

import psutil
import os
import os.path as op
import logging
from pathlib import Path


logger = logging.getLogger(__name__)


def make_shortcut(pkgname, script_path, title):
    """Create a desktop shortcut that runs a script in the currently active
    conda environment. pkgname is the package name and script is the path relative
    to the package directory, e.g. gui/mygui.py"""
    try:
        import win32com.client
    except ImportError:
        logger.warning('not on Windows system, cannot create shortcut (yet)')
        return

    # home = Path.home()  # Py3 pathtools only
    home = Path(os.path.expanduser('~'))
    desktop = home / 'Desktop'
    link_filename = '%s.lnk' % title
    link_path = desktop / link_filename

    # for some reason CONDA_ROOT is not set, so get root from executable path
    anaconda_python = Path(os.environ['CONDA_PYTHON_EXE'])
    envdir = Path(os.environ['CONDA_PREFIX'])
    anaconda_root = anaconda_python.parent

    pythonw = anaconda_root / 'pythonw.exe'  # the base interpreter
    cwp = anaconda_root / 'cwp.py'
    pythonw_env = envdir / 'pythonw.exe'  # the env-specific interpreter
    # tentative script path
    script = envdir / 'Lib' / 'site-packages' / pkgname / script_path

    if not script.is_file():
        # may be a 'development' install (e.g. pip -e)
        # hack: try reading from egg link
        logger.debug('trying to read egg link')
        egg_link_file = envdir / 'Lib' / 'site-packages' / (pkgname + '.egg-link')
        if egg_link_file.exists():
            with egg_link_file.open() as f:
                pkg_path = Path(f.read().splitlines()[0])
            if pkg_path.is_dir():
                script = pkg_path / pkgname / script_path
                if not script.is_file():
                    raise OSError(
                        'cannot find script file under site-packages or egg link'
                    )
            else:
                raise OSError('path in egg link %s not found' % pkg_path)

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
                        logger.debug('found running process %s' % cmdline[1])
                        nprocs += 1
                        if nprocs == 2:
                            logger.debug('found 2 running processes (or more)')
                            return True
        # catch NoSuchProcess for procs that disappear inside loop
        except (psutil.AccessDenied, psutil.NoSuchProcess):
            pass
    logger.debug('found 1 process or less')
    return False
