import hashlib
import os
import shutil
import sys
import tarfile

import socks5man

global _path
_path = os.path.expanduser("~/.socks5man")

def create_cwd():
    if not os.path.isdir(_path):
        os.mkdir(_path)

    for dir in os.listdir(cwd(internal=True)):
        if not os.path.exists(cwd(dir)):
            shutil.copytree(cwd(dir, internal=True), cwd(dir))

    with tarfile.open(cwd("geodb", "geodblite.tar.gz")) as tar:
        unpack_mmdb(tar, cwd("geodb", "extracted", "geodblite.mmdb"))

    geodb_hash = md5(cwd("geodb", "geodblite.tar.gz"))
    with open(cwd("geodb", ".version"), "wb") as fw:
        fw.write(geodb_hash)

def md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        while True:
            chunk = f.read(4096)
            if not chunk:
                break
            hash_md5.update(chunk)

    return hash_md5.hexdigest()

def unpack_mmdb(tar, to):
    for member in tar:
        if not member.isfile():
            continue

        if os.path.splitext(member.name)[1] == ".mmdb":
            with open(to, "wb") as fw:
                shutil.copyfileobj(tar.fileobj, fw, member.size)
            break

def cwd(*args, **kwargs):
    if kwargs.get("internal"):
        return os.path.join(socks5man.__path__[0], "setupdata", *args)

    if not os.path.isdir(_path):
        os.mkdir(_path)
        create_cwd()

    return os.path.join(_path, *args)

def color(text, color_code):
    """Colorize text.
    @param text: text.
    @param color_code: color.
    @return: colorized text.
    """
    if sys.platform == "win32" and os.getenv("TERM") != "xterm":
        return text
    return "\x1b[%dm%s\x1b[0m" % (color_code, text)

def red(text):
    return color(text, 31)

def yellow(text):
    return color(text, 33)
