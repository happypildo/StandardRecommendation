# Generated by Django 4.2.16 on 2024-11-24 14:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('news', '0006_topkeywords'),
    ]

    operations = [
        migrations.AddField(
            model_name='useraction',
            name='num_of_clicks',
            field=models.IntegerField(default=0),
        ),
    ]
