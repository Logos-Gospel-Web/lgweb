_model_names = ['contact', 'analytics']

def _route_db(model_name):
    if model_name in _model_names:
        return model_name
    return None

class DbRouter:
    def db_for_read(self, model, **hints):
        return _route_db(model._meta.model_name)

    def db_for_write(self, model, **hints):
        return _route_db(model._meta.model_name)

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        r = _route_db(model_name) or 'default'
        return r == db
