from django.db import migrations

def get_levels_data():
    return [
        {
            "title": "Welcome to TypeCat",
            "content_text": "Welcome to the world of TypeCat! Use your keyboard to run through different challenges and become the greatest typist of all time. Stay sharp and type fast.",
            "base_reward": 10,
            "difficulty_multiplier": 1.0,
        },
        {
            "title": "Quick Sprint",
            "content_text": "A fast sprint requires quick fingers. Do not hesitate. Type as rapidly as you can without looking back.",
            "base_reward": 15,
            "difficulty_multiplier": 1.2,
        },
        {
            "title": "The Long Marathon",
            "content_text": "Marathons are a test of endurance rather than pure speed. You must maintain a steady rhythm, calm breathing, and incredible focus. Typists who rush early will find their accuracy dropping as sentences become longer and words more complex. Keep your wrists relaxed and push through the mental fatigue. The finish line is far, but consistency will guide you there safely.",
            "base_reward": 50,
            "difficulty_multiplier": 1.5,
        },
        {
            "title": "Special Characters",
            "content_text": "Ready? $100 for the winner! However, 50% of the contestants fail at the first hurdle. Email john.doe@example.com by 2:00 PM if you want to join the [elite] bracket. Don't forget your #1 priority: typing accurately!",
            "base_reward": 25,
            "difficulty_multiplier": 1.8,
        },
        {
            "title": "Left Hand Isolation",
            "content_text": "we refer drew reserved fawces exacted exact traces effect ever free raw sacred secret cats cars fear extra few races fact saw target test sweet wear tab red base care case drew",
            "base_reward": 12,
            "difficulty_multiplier": 1.1,
        },
        {
            "title": "Right Hand Isolation",
            "content_text": "july john lily pooh loop poop plum poll minimum monk noun poly pony ill imp ink look loom milo nip pop puppy pink pulp oily hook hoop kill",
            "base_reward": 12,
            "difficulty_multiplier": 1.1,
        },
        {
            "title": "Numeric Chaos",
            "content_text": "In 1995, over 23456 people registered for the event. The stock rose by 45.67%, leading to a profit of 8912 dollars per share. You have 30 seconds to decode the massive grid: 123984 5590 192837 4001.",
            "base_reward": 40,
            "difficulty_multiplier": 1.9,
        },
        {
            "title": "Poetry Practice",
            "content_text": "The woods are lovely, dark and deep, But I have promises to keep, And miles to go before I sleep, And miles to go before I sleep.",
            "base_reward": 20,
            "difficulty_multiplier": 1.2,
        },
        {
            "title": "Corporate Lingo",
            "content_text": "Let us circle back on the deliverables to ensure synergy across the enterprise platform. We must leverage our core competencies to drive paradigm shifts in the consumer pipeline. Actionable insights will dictate the overall bandwidth required.",
            "base_reward": 22,
            "difficulty_multiplier": 1.4,
        },
        {
            "title": "Cat Survival Mini",
            "content_text": "Meow hiss purr pounce leap climb sleep eat run chase mouse yarn laser nap wake stretch claw scratch bite hunt meow hiss purr.",
            "base_reward": 8,
            "difficulty_multiplier": 1.0,
        },
        {
            "title": "Advanced Programming Syntax",
            "content_text": "function calculate(x, y) { return x >= y ? (x * y) + 100 : Math.floor(y / x); } const arr = [1, 2, 3]; arr.map(a => calculate(a, 10));",
            "base_reward": 45,
            "difficulty_multiplier": 2.2,
        },
        {
            "title": "Foreign Loanwards",
            "content_text": "He loved eating croissants and pain au chocolat at the boutique cafe. The entrepreneur possessed a certain je ne sais quoi, capturing the zeitgeist of the era perfectly.",
            "base_reward": 28,
            "difficulty_multiplier": 1.6,
        },
        {
            "title": "Scientific Literature",
            "content_text": "Mitochondria are often referred to as the powerhouses of the cell. They generate most of the cell's supply of adenosine triphosphate, used as a source of chemical energy.",
            "base_reward": 30,
            "difficulty_multiplier": 1.5,
        },
        {
            "title": "Short Story Extract",
            "content_text": "The wind howled outside the brittle glass window. She pulled her blanket tighter, staring at the flickering candlelight. A sudden knock shattered the silence.",
            "base_reward": 18,
            "difficulty_multiplier": 1.1,
        },
        {
            "title": "Capitalization Mayhem",
            "content_text": "WHY ARE YOU YELLING? I Am Not Yelling, I Just Prefer Formatting My Text With CamelCase And TitleCase Randomly. iTs So Co0l t0 BrEAk rULeS.",
            "base_reward": 35,
            "difficulty_multiplier": 1.7,
        },
        {
            "title": "Tongue Twisters",
            "content_text": "Peter Piper picked a peck of pickled peppers. She sells seashells by the seashore. How much wood would a woodchuck chuck if a woodchuck could chuck wood?",
            "base_reward": 24,
            "difficulty_multiplier": 1.4,
        },
        {
            "title": "Philosophical Musings",
            "content_text": "I think, therefore I am. To be or not to be, that is the question. We are what we repeatedly do; excellence, then, is not an act but a habit.",
            "base_reward": 26,
            "difficulty_multiplier": 1.3,
        },
        {
            "title": "Rapid Symbols",
            "content_text": "@@#! ***&&& ^^^ %%% $$$ (___) === +++ /// \\\\\\ ||| >>> <<< ???",
            "base_reward": 50,
            "difficulty_multiplier": 2.5,
        },
        {
            "title": "Double Consonants",
            "content_text": "Accommodation committee embarrass millennium successfully accommodate parallel necessary professional occurrences occasion.",
            "base_reward": 20,
            "difficulty_multiplier": 1.4,
        },
        {
            "title": "The Final Trial",
            "content_text": "Congratulations on making it this far. To finish your journey, you must type flawlessly. Every letter counts. 1 2 3 GO! Speed, precision, and accuracy merge into perfection. You are the ultimate typer.",
            "base_reward": 100,
            "difficulty_multiplier": 3.0,
        }
    ]

def seed_levels(apps, schema_editor):
    Level = apps.get_model('levels', 'Level')

    if Level.objects.exists():
        # Repair: fix any levels seeded with cost=0 by a prior version
        for entry in get_levels_data():
            Level.objects.filter(text=entry["content_text"], cost=0).update(
                cost=entry["base_reward"]
            )
        return

    for entry in get_levels_data():
        difficulty = float(entry.get("difficulty_multiplier", 1.0))
        goal_wpm = max(20, min(140, int(40 * difficulty)))
        Level.objects.create(
            text=entry["content_text"],
            cost=entry["base_reward"],
            goal_wpm=goal_wpm,
        )

class Migration(migrations.Migration):

    dependencies = [
        ('levels', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(seed_levels, reverse_code=migrations.RunPython.noop),
    ]
