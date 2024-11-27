from django.apps import AppConfig


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    
    def ready(self):
        from config.scheduler import start, start_notify
        start()
        start_notify()
