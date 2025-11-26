from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("inspection_management", "0057_hseplanner"),
    ]

    operations = [
        migrations.AlterField(
            model_name="risklevel",
            name="value",
            field=models.CharField(max_length=50),
        ),
    ]

