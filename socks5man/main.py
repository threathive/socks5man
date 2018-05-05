from socks5man.manager import Manager
import logging

logging.basicConfig(level=logging.DEBUG)

if __name__ == "__main__":
    m = Manager()

    # b = [
    #     {
    #         "host":"192.168.1.1",
    #         "port": 8231
    #     },
    #     {
    #         "host": "cuckoo.rznet.nl",
    #         "port": 12802,
    #         "password": "Hallo",
    #         "username": "Doei"
    #     },
    #     {
    #         "host": "security.nl",
    #         "port": 8231
    #     },
    #     {
    #         "host": "115.132.114.252",
    #         "port": 8181,
    #         "description": "Very koel socks"
    #     }
    # ]
    #m.bulk_add(b, description="Dag")

    p = []

    # for prox in a.split("\n"):
    #     ip, port = prox.split(":")
    #     p.append({
    #         "host": ip,
    #         "port": int(port)
    #     })
    #
    # m.bulk_add(p)
    import win_inet_pton
    from socks5man.database import Database
    from socks5man.socks5 import Socks5
    l = Database().list_socks5()
    print l

    for s in l:
        print "Trying: %s" % s.host
        try:
            if Socks5(s).verify():
                print "Working: %s" % s
        except Exception:
            pass