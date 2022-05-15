from .manager import ApiModelManager

class MailusersManager(ApiModelManager):
    def __init__(self, api):
        self.model_name        = 'mailuser'
        self.model_name_plural = 'mailusers'
        self.is_instantaneous  = False
        self.primary_key       = 'id'
        super().__init__(api)

    def list_all(self, *args, **kwargs):   return super().list_all(*args, **kwargs)
    def read(self, *args, **kwargs):       return super().read(*args, **kwargs)
    def create(self, *args, **kwargs):     return super().create(*args, **kwargs)
    def create_one(self, *args, **kwargs): return super().create_one(*args, **kwargs)
    def update(self, *args, **kwargs):     return super().update(*args, **kwargs)
    def update_one(self, *args, **kwargs): return super().update_one(*args, **kwargs)
    def delete(self, *args, **kwargs):     return super().delete(*args, **kwargs)
    def delete_one(self, *args, **kwargs): return super().delete_one(*args, **kwargs)

    def check_equals(self, a, b):
        return ( a['name'] == b['name'] and
                 a['imap_server'] == b['imap_server'] )

    def check_obstructs(self, existing, new):
        return False

    def check_satisfies(self, existing, new):
        return self.check_equals(new, existing)
