import os
import stat


def chmod_executable(filename):
    mode = os.stat(filename).st_mode
    new_mode = mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH
    if new_mode != mode:
        os.chmod(filename, new_mode)
