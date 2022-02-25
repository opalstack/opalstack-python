from .manager import ApiModelManager

class DnsrecordsManager(ApiModelManager):
    def __init__(self, api):
        self.model_name        = 'dnsrecord'
        self.model_name_plural = 'dnsrecords'
        super().__init__(api)

    def list_all(self, *args, **kwargs): return super().list_all(*args, **kwargs)
    def read(self, *args, **kwargs):     return super().read(*args, **kwargs)
    def create(self, *args, **kwargs):   return super().create(*args, **kwargs)
    def update(self, *args, **kwargs):   return super().update(*args, **kwargs)
    def delete(self, *args, **kwargs):   return super().delete(*args, **kwargs)

    def check_equals(self, a, b):
        if 'domain_name' not in a: return False
        if 'domain_name' not in b: return False
        return ( a['domain_name'] == b['domain_name'] and
                 a['type'] == b['type'] and
                 a['content'] == b['content'] )

    def check_obstructs(self, existing, new):
        return False

    def check_satisfies(self, existing, new):
        return self.check_equals(new, existing)
