# Generated by Django 3.2.5 on 2021-10-13 06:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('findiff', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='book_pages',
            field=models.IntegerField(blank=True, default=0, verbose_name='书籍页数'),
        ),
    ]