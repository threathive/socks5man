import logging

class Logger:
    @staticmethod
    def setup_logger():
        logformat  = "[%(asctime)s %(levelname)s] %(message)s"
        dateformat = "%d-%m-%y %H:%M:%S"

        logging.basicConfig(filename="socks5man.log", filemode='a', format=logformat,  datefmt=dateformat, level=logging.INFO)
        console           = logging.StreamHandler()
        formatter         = logging.Formatter(logformat)
        formatter.datefmt = dateformat
        
        console.setFormatter(formatter)
        logging.getLogger().addHandler(console)