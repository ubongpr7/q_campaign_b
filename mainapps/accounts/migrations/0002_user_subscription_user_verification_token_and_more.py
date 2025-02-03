# Generated by Django 5.1.5 on 2025-02-03 09:35

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('stripe_pay', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='subscription',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='stripe_pay.subscription'),
        ),
        migrations.AddField(
            model_name='user',
            name='verification_token',
            field=models.CharField(blank=True, max_length=255, null=True),
        ),
        migrations.DeleteModel(
            name='VerificationCode',
        ),
    ]
