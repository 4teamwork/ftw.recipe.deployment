import os
import stat


def chmod_executable(filename):
    mode = os.stat(filename).st_mode
    mode = mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    os.chmod(filename, mode)
