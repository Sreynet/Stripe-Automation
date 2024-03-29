# Generated by Django 4.2.7 on 2023-11-07 00:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webhook', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='discordEmail',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='stripeEmail',
            field=models.EmailField(max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='subscriptionStatus',
            field=models.CharField(max_length=50, null=True),
        ),
        migrations.AddField(
            model_name='user',
            name='userCode',
            field=models.CharField(max_length=50, null=True),
        ),
    ]
