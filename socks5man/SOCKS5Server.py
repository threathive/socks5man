import time
import uuid

from socks5man.TestSOCKS5 import TestSOCKS5

class SOCKS5Server:
    def __init__(self):
        self.identifier    = str(uuid.uuid4())
        self.active        = False
        self.port          = None
        self.ip            = None
        self.password      = None
        self.username      = None
        self.last_used     = 0
        self.last_checked  = 0
        self.country       = None
        
        self.settings_json = {}
    
    def is_authenticated(self):
        '''Returns true if a username/password is needed for this server'''
        
        if self.password is not None or self.username is not None:
            return True
        return False
    
    def is_active(self):
        '''Tests if this SOCKS5 server is still operating'''
        
        test_connection = TestSOCKS5(self.ip, self.port,
                                     self.username, self.password)
        
        if test_connection.test():
            self.active = True
            self._update_last_checked_time()
            return True
        return False
    
    def _update_last_checked_time(self):
        '''Updates the last checked time to current time in seconds'''
        
        self.last_checked = time.mktime(time.gmtime())
    
    def update_last_used_time(self):
        '''Updates the last used time to current time in seconds'''
        
        self.last_used = time.mktime(time.gmtime())
    
    def get_human_last_used_time(self):
        '''Returns a human readable string of the last date/time used'''
        
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.last_used))
    
    def get_human_last_checked_time(self):
        '''Returns a human readable string of the last date/time checked'''
        
        return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime(self.last_checked))

    def get_json_settings(self):
        
        self.settings_json["id"]            = self.identifier
        self.settings_json["active"]        = self.active
        self.settings_json["ip"]            = self.ip
        self.settings_json["port"]          = self.port
        self.settings_json["authenticated"] = self.is_authenticated()
        self.settings_json["username"]      = self.username
        self.settings_json["password"]      = self.password
        self.settings_json["last_used"]     = self.get_human_last_used_time()
        self.settings_json["last_checked"]  = self.get_human_last_checked_time()
        self.settings_json["country"]       = self.country
    
        return self.settings_json
