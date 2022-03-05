from .manager import ApiModelManager

class ServersManager(ApiModelManager):
    def __init__(self, api):
        self.model_name        = 'server'
        self.model_name_plural = 'servers'
        self.is_instantaneous  = True
        self.primary_key       = 'id'
        super().__init__(api)

    def list_all(self, *args, **kwargs): return super().list_all(*args, **kwargs)
    def read(self, *args, **kwargs):     return super().read(*args, **kwargs)

    def check_equals(self, a, b):
        return ( a['id'] == b['id'] )

    def check_obstructs(self, existing, new):
        return False

    def check_satisfies(self, existing, new):
        return False
