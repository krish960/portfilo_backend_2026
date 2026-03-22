import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_builder.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(email="admin@gmail.com").exists():
    User.objects.create_superuser(
        email="thombarek362@gmail.com",
        password="admin123"
    )