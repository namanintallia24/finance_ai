# finance_project/db_router.py

class DatabaseRouter:
    """
    Routes models in the 'ai_data' app to 'finance_ai' DB.
    All other apps use default.
    """
    route_app_labels = {'ai_data'}

    def db_for_read(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'finance_ai'
        return None

    def db_for_write(self, model, **hints):
        if model._meta.app_label in self.route_app_labels:
            return 'finance_ai'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        if (
            obj1._meta.app_label in self.route_app_labels or
            obj2._meta.app_label in self.route_app_labels
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        if app_label in self.route_app_labels:
            return db == 'finance_ai'
        if db == 'finance_ai':
            return False
        return None
