import os
import shutil

import socks5man

global _path
_path = os.path.expanduser("~/.socks5man")

def create_cwd():
    if not os.path.isdir(_path):
        os.mkdir(_path)

    for dir in os.listdir(cwd(internal=True)):
        if not os.path.exists(cwd(dir)):
            shutil.copytree(cwd(dir, internal=True), cwd(dir))

def cwd(*args, **kwargs):
    if kwargs.get("internal"):
        return os.path.join(socks5man.__path__[0], "setupdata", *args)

    if not os.path.isdir(_path):
        os.mkdir(_path)
        create_cwd()

    return os.path.join(_path, *args)
