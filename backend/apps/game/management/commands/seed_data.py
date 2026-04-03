import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from apps.accounts.models import Avatar, Profile
from apps.game.models import Level, Attempt
from django.core.files import File
import os

class Command(BaseCommand):
    help = 'Seeds the database with avatars, levels, and dummy users.'

    def handle(self, *args, **options):
        self.stdout.write("Seeding data...")

        # 1. Create Avatars
        avatars_data = [
            {'name': 'Ginger', 'path': 'avatars/ginger.png'},
            {'name': 'Tuxedo', 'path': 'avatars/tuxedo.png'},
            {'name': 'Tabby', 'path': 'avatars/tabby.png'},
        ]
        
        avatar_objs = []
        for a in avatars_data:
            avatar, created = Avatar.objects.get_or_create(name=a['name'])
            if created:
                avatar.image = a['path']
                avatar.save()
                self.stdout.write(f"Created avatar: {a['name']}")
            avatar_objs.append(avatar)

        # 2. Create Levels
        levels_data = [
            {
                'title': 'Easy Start',
                'content_text': 'The quick brown fox jumps over the lazy dog.',
                'mode': 'standard',
                'difficulty': 1,
                'base_reward': 50
            },
            {
                'title': 'Coding Basics',
                'content_text': 'import os\nimport sys\n\ndef hello_world():\n    print("Hello, user!")',
                'mode': 'standard',
                'difficulty': 2,
                'base_reward': 100
            },
            {
                'title': 'Cat Adventure: The Kitchen',
                'content_text': 'You wake up in a sunny kitchen. There is a bowl of fish on the counter. Do you JUMP or MEOW?',
                'mode': 'cat_survival',
                'difficulty': 1,
                'base_reward': 75
            },
            {
                'title': 'Cat Adventure: The Garden',
                'content_text': 'The dog is barking at the fence. Behind you is a large oak tree. Do you CLIMB or HIDE?',
                'mode': 'cat_survival',
                'difficulty': 2,
                'base_reward': 150
            },
            {
                'title': 'Advanced Poetry',
                'content_text': 'The woods are lovely, dark and deep, but I have promises to keep, and miles to go before I sleep.',
                'mode': 'standard',
                'difficulty': 3,
                'base_reward': 200
            }
        ]

        for ld in levels_data:
            level, created = Level.objects.get_or_create(title=ld['title'], defaults=ld)
            if created:
                self.stdout.write(f"Created level: {ld['title']}")

        # 3. Create Sample Users
        user_names = ['speedy_cat', 'type_master', 'keyboard_ninja', 'slow_and_steady']
        for name in user_names:
            user, created = User.objects.get_or_create(username=name)
            if created:
                user.set_password('password123')
                user.save()
                
                profile = user.profile
                profile.avatar = random.choice(avatar_objs)
                profile.save()
                self.stdout.write(f"Created user: {name}")

                # Create some random attempts only if the user has none
                if not Attempt.objects.filter(profile=profile).exists():
                    levels = Level.objects.all()
                    for _ in range(3):
                        level = random.choice(levels)
                        wpm = random.uniform(20, 120)
                        accuracy = random.uniform(80, 100)
                        earned = int(level.base_reward * (accuracy / 100))
                        
                        Attempt.objects.create(
                            profile=profile,
                            level=level,
                            wpm=wpm,
                            accuracy=accuracy,
                            earned_score=earned
                        )
                        profile.award(earned, wpm)

        self.stdout.write(self.style.SUCCESS('Successfully seeded database.'))
