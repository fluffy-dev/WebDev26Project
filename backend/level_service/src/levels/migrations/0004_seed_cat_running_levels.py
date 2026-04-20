from django.db import migrations


def get_cat_running_levels_data():
    return [
        {
            "title": "Forest Dash One",
            "content_text": "The cat sprints over branches, keeping balance, speed, and focus while leaves scatter below.",
            "base_reward": 12,
            "difficulty_multiplier": 1.0,
        },
        {
            "title": "Moonlit Sprint",
            "content_text": "Moonlight flashes across the canopy as the cat leaps from limb to limb without slowing down.",
            "base_reward": 14,
            "difficulty_multiplier": 1.1,
        },
        {
            "title": "Branch Breaker",
            "content_text": "A missed branch means trouble, so the cat keeps moving fast and lands every jump with care.",
            "base_reward": 16,
            "difficulty_multiplier": 1.2,
        },
        {
            "title": "Whisker Wind",
            "content_text": "Wind pushes hard through the trees, but the cat runs on, paws tapping a steady rhythm overhead.",
            "base_reward": 18,
            "difficulty_multiplier": 1.3,
        },
        {
            "title": "Pounce Path",
            "content_text": "Every branch is a step forward, and every step asks the cat to be faster than the falling dusk.",
            "base_reward": 20,
            "difficulty_multiplier": 1.4,
        },
        {
            "title": "High Canopy Chase",
            "content_text": "The cat dashes through the high canopy, weaving around bark, moss, and swinging vines.",
            "base_reward": 22,
            "difficulty_multiplier": 1.5,
        },
        {
            "title": "Silent Landing",
            "content_text": "No one hears the cat land as it crosses each branch, one quick move after another.",
            "base_reward": 24,
            "difficulty_multiplier": 1.6,
        },
        {
            "title": "Twilight Escape",
            "content_text": "Twilight closes in, and the cat must outrun every obstacle before the forest goes dark.",
            "base_reward": 26,
            "difficulty_multiplier": 1.7,
        },
        {
            "title": "Rapid Tail Chase",
            "content_text": "The cat races the wind, tail high, paws light, and every branch demands perfect timing.",
            "base_reward": 28,
            "difficulty_multiplier": 1.8,
        },
        {
            "title": "Final Leap",
            "content_text": "One last leap remains, and the cat must keep pace or tumble back into the dark below.",
            "base_reward": 30,
            "difficulty_multiplier": 2.0,
        },
    ]


def seed_cat_running_levels(apps, schema_editor):
    Level = apps.get_model("levels", "Level")

    for entry in get_cat_running_levels_data():
        if Level.objects.filter(text=entry["content_text"]).exists():
            continue

        difficulty = float(entry.get("difficulty_multiplier", 1.0))
        goal_wpm = max(20, min(140, int(40 * difficulty)))
        Level.objects.create(
            text=entry["content_text"],
            cost=entry["base_reward"],
            goal_wpm=goal_wpm,
            level_type="cat_running",
        )


class Migration(migrations.Migration):

    dependencies = [
        ("levels", "0003_level_type"),
    ]

    operations = [
        migrations.RunPython(seed_cat_running_levels, reverse_code=migrations.RunPython.noop),
    ]