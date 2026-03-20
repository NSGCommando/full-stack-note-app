from typing import Dict

class UserView():
    @staticmethod
    def to_dict(query_res)->Dict[str,int|str|bool]:
        """Serializer to convert a User query response object into a Dictionary.
        Return Example: {id:1,username:'admin',is_admin:True}"""
        assert isinstance(query_res.id,int), "User ID should be 'int', check query"
        assert isinstance(query_res.is_admin,bool), "'is_admin' should be 'bool', check query"
        return {"id"        :query_res.id,
                "username"  :str(query_res.user_name),
                "is_admin"  :query_res.is_admin}

class UserNotesView():
    @staticmethod
    def to_dict(query_res)->Dict[str,int|str]:
        """Serializer to convert a Notes query response object into a Dictionary"""
        assert isinstance(query_res.id,int), "Note ID should be 'int', check query"
        assert isinstance(query_res.note,str), "Note cannot be non-string, check query"
        return {"id"        :query_res.id,
                "note"      :query_res.note,
                "timestamp" :str(query_res.timestamp)}