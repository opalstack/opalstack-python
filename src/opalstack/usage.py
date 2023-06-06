from .manager import ApiModelManager

class UsageManager(ApiModelManager):
    def __init__(self, api):
        self.model_name        = 'usage'
        self.model_name_plural = 'usages'
        self.is_instantaneous  = True
        self.primary_key       = None
        super().__init__(api)

    def webusage_latest(self, embed=[]):
        qs = ('?embed=' + ','.join(embed)) if embed else ''
        return self.api.http_get_result(f'/{self.model_name}/web/latest/{qs}', ensure_status=[200])

    def mailusage_latest(self, embed=[]):
        qs = ('?embed=' + ','.join(embed)) if embed else ''
        return self.api.http_get_result(f'/{self.model_name}/mail/latest/{qs}', ensure_status=[200])

    def check_equals(self, a, b):
        return ( a['id'] == b['id'] )

    def check_obstructs(self, existing, new):
        return False

    def check_satisfies(self, existing, new):
        return False
