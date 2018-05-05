class Socks5manError(Exception):
    """Error that halts socks5man"""

class Socks5CreationError(Socks5manError):
    """Errors specifically related to the creation of new socks5 servers"""