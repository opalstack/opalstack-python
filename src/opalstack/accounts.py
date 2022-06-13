from .manager import ApiModelManager

class AccountsManager(ApiModelManager):
    def __init__(self, api):
        self.model_name        = 'account'
        self.model_name_plural = 'accounts'
        self.is_instantaneous  = False
        self.primary_key       = 'id'
        super().__init__(api)

    def list_all(self, *args, **kwargs):   return super().list_all(*args, **kwargs)
    def read(self, *args, **kwargs):       return super().read(*args, **kwargs)
    def update(self, *args, **kwargs):     return super().update(*args, **kwargs)
    def update_one(self, *args, **kwargs): return super().update_one(*args, **kwargs)

    def check_equals(self, a, b):
        return ( a['id'] == b['id'] )

    def check_obstructs(self, existing, new):
        return False

    def check_satisfies(self, existing, new):
        return False
