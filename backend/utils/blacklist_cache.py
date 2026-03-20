import threading, time
from typing import Dict
class BlacklistCache:
    def __init__(self):
        self._data:Dict[str,float] = {}
        self._lock = threading.Lock() # lock to ensure only one thread can execult at a time
        # shared between all methods of any particular instance of the BlacklistCache
        # No method is supposed to try changing the object dict before acquiring the lock, even the Cleaner
        self.start_cleanup_thread() # start cleanup thread on blacklist initialization itself

    def add_jti(self,jti:str,expiry_in_secs:int|float):
        """Method to add a JTI to blacklist with remaining expiration time"""
        expiry = time.time()+expiry_in_secs
        with self._lock: # only touch the dict after acquiring the lock
            self._data[jti] = expiry

    def check_blacklist(self,jti:str):
        """Method to check if a JTI is blacklisted or not"""
        with self._lock: # only touch the dict after acquiring the lock
            expiry = self._data.get(jti)
            if expiry is None:return False # if token already expired, no need to say blacklisted
            if expiry>time.time():return True # say blacklisted if the token is in the dict and not yet expired
            else: return False # Say NOT BLACKLISTED because it's expired, not blacklisted. Other checks will reject it

    def _cleanup(self):
        """internal method to delete expired tokens"""
        while(True):
            time.sleep(120)
            curr_time = time.time()
            with self._lock: # only touch the dict after acquiring the lock
                # collect all items to delete via a read op
                delete_list = [jti for jti,expiry in self._data.items() if expiry<=curr_time]
            if delete_list:
                with self._lock:
                    for jti in delete_list:
                        self._data.pop(jti,None) # Use default as 'None' to prevent crashes on key errors
    
    def start_cleanup_thread(self):
        cleaner = threading.Thread(target=self._cleanup,daemon=True) # daemon=True alalows this to run in main task's background
        cleaner.start()