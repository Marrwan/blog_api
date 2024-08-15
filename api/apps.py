from django.apps import AppConfig

class BlogConfig(AppConfig):
    name = 'api'

    def ready(self):
        import api.signals
