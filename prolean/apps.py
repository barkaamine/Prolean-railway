# apps.py
from django.apps import AppConfig

class proleanConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'prolean'
    
    def ready(self):
        # Import signals if you have any
        try:
            import prolean.signals
        except ImportError:
            pass