# Generated by Django 4.2.7 on 2023-11-25 01:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('grades', '0004_alter_submission_score'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='file',
            field=models.FileField(upload_to='uploads/'),
        ),
    ]
