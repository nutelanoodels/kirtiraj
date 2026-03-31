from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('products', '0008_auto_20260324_1953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='image',
            field=models.URLField(blank=True, max_length=500, null=True),
        ),
    ]
