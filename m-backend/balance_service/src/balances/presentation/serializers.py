from rest_framework import serializers


class BalanceSerializer(serializers.Serializer):
    """Serialises a user's current balance."""

    id = serializers.UUIDField()
    user_id = serializers.UUIDField()
    balance = serializers.IntegerField()
    updated_at = serializers.DateTimeField()


class TransactionSerializer(serializers.Serializer):
    """Serialises a single transaction record."""

    id = serializers.UUIDField()
    event_id = serializers.UUIDField()
    amount = serializers.IntegerField()
    type = serializers.CharField()
    created_at = serializers.DateTimeField()


class TransactionListSerializer(serializers.Serializer):
    """Serialises a paginated transaction list."""

    count = serializers.IntegerField()
    results = TransactionSerializer(many=True)
