import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')
django.setup()

from django.contrib.auth.models import User

try:
    admin = User.objects.get(username='admin')
    print(f"Admin user exists: True")
    print(f"Is superuser: {admin.is_superuser}")
    print(f"Is active: {admin.is_active}")
except User.DoesNotExist:
    print("Admin user exists: False")
except Exception as e:
    print(f"Error: {e}")
