from .manager import ApiModelManager

class CertsManager(ApiModelManager):
    def __init__(self, api):
        self.model_name        = 'cert'
        self.model_name_plural = 'certs'
        self.is_instantaneous  = True
        self.primary_key       = 'id'
        super().__init__(api)

    def list_all(self, *args, **kwargs): return super().list_all(*args, **kwargs)
    def read(self, *args, **kwargs):     return super().read(*args, **kwargs)
    def create(self, *args, **kwargs):   return super().create(*args, **kwargs)
    def update(self, *args, **kwargs):   return super().update(*args, **kwargs)
    def delete(self, *args, **kwargs):   return super().delete(*args, **kwargs)

    def check_equals(self, a, b):
        return ( a['name'] == b['name'] and
                 a['cert'] == b['cert'] and
                 a['intermediates'] == b['intermediates'] and
                 a['key'] == b['key'] )

    def check_obstructs(self, existing, new):
        return False

    def check_satisfies(self, existing, new):
        return self.check_equals(new, existing)