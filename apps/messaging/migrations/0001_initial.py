import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('portfolios', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContactMessage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sender_name', models.CharField(max_length=200)),
                ('sender_email', models.EmailField(max_length=254)),
                ('subject', models.CharField(blank=True, max_length=300)),
                ('message', models.TextField()),
                ('is_read', models.BooleanField(default=False)),
                ('sent_at', models.DateTimeField(auto_now_add=True)),
                ('portfolio', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='messages', to='portfolios.portfolio')),
            ],
            options={'ordering': ['-sent_at']},
        ),
    ]
