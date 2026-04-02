from django.contrib.auth.models import User
from apps.game.models import Level

if not User.objects.filter(is_superuser=True).exists():
    User.objects.create_superuser('admin', 'admin@typecat.dev', 'admin1234')

levels = [
    dict(title='Hello World', content_text='the quick brown fox jumps over the lazy dog',
         mode='standard', base_reward=100, difficulty=1),
    dict(title='Code Sprint', content_text='def hello world print hello world',
         mode='standard', base_reward=150, difficulty=2),
    dict(title='Cat on a Branch', content_text='abcdefghijklmnopqrstuvwxyz',
         mode='cat_survival', base_reward=200, difficulty=3),
]

for l in levels:
    Level.objects.get_or_create(title=l['title'], defaults=l)

print('Seed complete.')
