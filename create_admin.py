import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

User = get_user_model()

def create_admin():
    username = 'admin'
    email = 'admin@example.com'
    password = 'admin'

    if not User.objects.filter(username=username).exists():
        User.objects.create_superuser(username, email, password)
        print(f"Superuser '{username}' created with password '{password}'")
    else:
        print(f"Superuser '{username}' already exists")

if __name__ == '__main__':
    create_admin()
