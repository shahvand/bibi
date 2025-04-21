# Generated manually

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0007_auto_20250414_2135'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='current_stock',
        ),
        migrations.RemoveField(
            model_name='product',
            name='min_stock',
        ),
    ] 