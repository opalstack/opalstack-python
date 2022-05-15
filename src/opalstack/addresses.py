from .manager import ApiModelManager

class AddressesManager(ApiModelManager):
    def __init__(self, api):
        self.model_name        = 'address'
        self.model_name_plural = 'addresses'
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
        return ( a['source'] == b['source'] and
                 a['destinations'] == b['destinations'] and
                 a['forwards'] == b['forwards'] )

    def check_obstructs(self, existing, new):
        return existing['source'] == new['source'] and not self.check_equals(new, existing)

    def check_satisfies(self, existing, new):
        return self.check_equals(new, existing)
