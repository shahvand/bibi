from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('workflow', '0011_alter_orderitem_approved_quantity_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='price_per_unit',
            field=models.DecimalField(decimal_places=0, max_digits=15, verbose_name='قیمت واحد'),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='requested_quantity',
            field=models.DecimalField(decimal_places=0, max_digits=15),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='approved_quantity',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=15, null=True),
        ),
        migrations.AlterField(
            model_name='orderitem',
            name='price_per_unit',
            field=models.DecimalField(blank=True, decimal_places=0, max_digits=15, null=True),
        ),
    ] 