import os
from django.db import migrations
from django.core.files import File
import logging

logger = logging.getLogger(__name__)

def seed_avatars(apps, schema_editor):
    ProfileImage = apps.get_model('users', 'ProfileImage')
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    avatars_dir = os.path.join(base_dir, 'avatars_seed')

    if not os.path.exists(avatars_dir):
        logger.warning(f"Avatars seed directory not found: {avatars_dir}")
        return

    # Check if there are already ProfileImages so we don't multiply them on pod restarts
    if ProfileImage.objects.exists():
        logger.info("Avatars already exist. Skipping seed.")
        return

    for filename in ['ninja.png', 'wizard.png', 'cyberpunk.png']:
        path = os.path.join(avatars_dir, filename)
        if os.path.exists(path):
            try:
                with open(path, 'rb') as f:
                    img = ProfileImage()
                    img.image.save(filename, File(f), save=True)
                logger.info(f"Seeded avatar: {filename}")
            except Exception as e:
                logger.error(f"Failed to seed avatar {filename}: {e}")

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_avatars, reverse_code=migrations.RunPython.noop),
    ]
