import os
import django
from django.contrib.auth.models import User

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Project.settings')
django.setup()

def create_admin():
    username = 'admin'
    email = 'admin@prolean.com'
    password = 'adminpassword123'
    
    if not User.objects.filter(username=username).exists():
        print(f"🚀 Creating superuser '{username}'...")
        User.objects.create_superuser(username, email, password)
        print(f"✅ Superuser created successfully!")
        print(f"   Username: {username}")
        print(f"   Password: {password}")
    else:
        print(f"ℹ️ Superuser '{username}' already exists.")

if __name__ == "__main__":
    create_admin()
