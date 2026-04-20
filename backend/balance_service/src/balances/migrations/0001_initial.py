import uuid
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Balance",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("user_id", models.UUIDField(db_index=True, unique=True)),
                ("balance", models.PositiveIntegerField(default=0)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "balances",
            },
        ),
        migrations.CreateModel(
            name="Transaction",
            fields=[
                (
                    "id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("event_id", models.UUIDField(unique=True)),
                (
                    "balance",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.PROTECT,
                        related_name="transactions",
                        to="balances.balance",
                    ),
                ),
                ("amount", models.PositiveIntegerField()),
                (
                    "type",
                    models.CharField(
                        choices=[("CREDIT", "Credit"), ("DEBIT", "Debit")],
                        max_length=6,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "db_table": "transactions",
                "ordering": ["-created_at"],
            },
        ),
    ]
