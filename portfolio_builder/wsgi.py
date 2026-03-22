import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portfolio_builder.settings')

application = get_wsgi_application()
from django.contrib.auth import get_user_model

User = get_user_model()

if not User.objects.filter(email="admin@gmail.com").exists():
    User.objects.create_superuser(
        email="thombarek362@gmail.com",
        password="admin123"
    )