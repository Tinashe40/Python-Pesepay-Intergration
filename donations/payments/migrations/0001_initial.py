# Generated by Django 5.1.4 on 2024-12-19 09:44

import django.db.models.deletion
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('payment_id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('reference_number', models.CharField(max_length=255, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Donation',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('amount', models.DecimalField(decimal_places=2, max_digits=10)),
                ('currency_code', models.CharField(max_length=10)),
                ('payment_reason', models.CharField(max_length=255)),
                ('status', models.CharField(default='Pending', max_length=50)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('payment', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='donation', to='payments.payment')),
            ],
        ),
    ]
