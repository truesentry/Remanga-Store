from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0003_product_category'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category',
            field=models.CharField(
                choices=[('manga', 'Манга'), ('manhwa', 'Манхва'), ('manhua', 'Маньхуа')],
                default='manga',
                max_length=50
            ),
        ),
        migrations.AddField(
            model_name='product',
            name='author',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='product',
            name='volume',
            field=models.PositiveIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='product',
            name='rating',
            field=models.DecimalField(decimal_places=1, default=0.0, max_digits=3),
        ),
        migrations.AddField(
            model_name='product',
            name='is_new',
            field=models.BooleanField(default=False),
        ),
    ]
