from backend.utils.blacklist_cache import BlacklistCache

_jwt_blacklist = None

def get_jwt_blacklist():
    """Getter for providing the same instance of blacklist. 
    Creates the instance once then always returns that same instance"""
    global _jwt_blacklist
    if _jwt_blacklist is None:
        _jwt_blacklist = BlacklistCache()
    return _jwt_blacklist