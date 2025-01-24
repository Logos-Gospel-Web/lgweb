_model_names = {
    'contact': 'contact',
    'analytics': 'analytics',
    'analyticstemp': 'analytics_temp',
}

def _route_db(model_name):
    return _model_names.get(model_name, None)

class DbRouter:
    def db_for_read(self, model, **hints):
        return _route_db(model._meta.model_name)

    def db_for_write(self, model, **hints):
        return _route_db(model._meta.model_name)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        r = _route_db(model_name) or 'default'
        return r == db
