# Generated by Django 5.1 on 2024-10-24 04:44

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0018_doctor_numreviews_doctor_rating'),
    ]

    operations = [
        migrations.AddField(
            model_name='doctor',
            name='perhourRate',
            field=models.DecimalField(decimal_places=2, default=0.0, max_digits=10),
        ),
    ]
