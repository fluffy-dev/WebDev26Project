from django.db import migrations, models


def backfill_level_type(apps, schema_editor):
    Level = apps.get_model("levels", "Level")
    Level.objects.filter(level_type__isnull=True).update(level_type="default")


class Migration(migrations.Migration):

    dependencies = [
        ("levels", "0002_seed_levels"),
    ]

    operations = [
        migrations.AddField(
            model_name="level",
            name="level_type",
            field=models.CharField(
                choices=[("default", "Default"), ("cat_running", "Cat Running")],
                default="default",
                max_length=32,
            ),
        ),
        migrations.RunPython(backfill_level_type, reverse_code=migrations.RunPython.noop),
    ]