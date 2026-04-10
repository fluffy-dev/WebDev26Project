from django.contrib import admin
from balances.infrastructure.models import Balance, Transaction

admin.site.register(Balance)
admin.site.register(Transaction)
