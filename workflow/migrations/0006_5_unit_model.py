# Generated manually to fix migration dependency issue

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0006_driver_notes'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50, unique=True, verbose_name='نام واحد')),
                ('symbol', models.CharField(max_length=10, verbose_name='نماد')),
            ],
            options={
                'verbose_name': 'واحد',
                'verbose_name_plural': 'واحدها',
                'ordering': ['name'],
            },
        ),
    ] 