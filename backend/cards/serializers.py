"""
Serializers for the Fintech Card Processing Platform.
Handles data validation and serialization/deserialization.
"""
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password
from .models import VirtualCard, Transaction, AccountSummary
from decimal import Decimal


class UserRegistrationSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )
    email = serializers.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password', 'password2')

    def validate(self, attrs):
        """Validate password match and email uniqueness"""
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError(
                {"password": "Password fields didn't match."}
            )

        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError(
                {"email": "A user with this email already exists."}
            )

        return attrs

    def create(self, validated_data):
        """Create and return a new user"""
        validated_data.pop('password2')
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            password=validated_data['password']
        )

        # Create account summary for new user
        AccountSummary.objects.create(user=user)

        return user


class UserSerializer(serializers.ModelSerializer):
    """Serializer for user details"""
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'date_joined')


class VirtualCardSerializer(serializers.ModelSerializer):
    """Serializer for virtual cards"""
    masked_card_number = serializers.ReadOnlyField()
    is_expired = serializers.ReadOnlyField()
    user_username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = VirtualCard
        fields = (
            'id',
            'user',
            'user_username',
            'card_number',
            'masked_card_number',
            'card_holder_name',
            'expiry_date',
            'cvv',
            'balance',
            'status',
            'is_expired',
            'created_at',
            'updated_at'
        )
        read_only_fields = ('id', 'card_number', 'cvv', 'balance', 'created_at', 'updated_at', 'user')
        extra_kwargs = {
            'card_number': {'write_only': True},
            'cvv': {'write_only': True},
        }

    def validate_card_holder_name(self, value):
        """Validate card holder name"""
        if not value or len(value.strip()) < 3:
            raise serializers.ValidationError(
                "Card holder name must be at least 3 characters long."
            )
        return value.strip().upper()

    def validate_status(self, value):
        """Validate status transitions"""
        if self.instance and self.instance.status == 'EXPIRED':
            raise serializers.ValidationError(
                "Cannot change status of an expired card."
            )
        return value


class VirtualCardCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating virtual cards"""
    initial_balance = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        required=False,
        default=Decimal('0.00'),
        min_value=Decimal('0.00')
    )

    class Meta:
        model = VirtualCard
        fields = ('card_holder_name', 'initial_balance')

    def create(self, validated_data):
        """Create a new virtual card"""
        initial_balance = validated_data.pop('initial_balance', Decimal('0.00'))
        user = self.context['request'].user

        card = VirtualCard.objects.create(
            user=user,
            card_holder_name=validated_data['card_holder_name'],
            balance=initial_balance
        )

        # Update user's account summary
        summary, _ = AccountSummary.objects.get_or_create(user=user)
        summary.update_summary()

        return card


class TransactionSerializer(serializers.ModelSerializer):
    """Serializer for transactions"""
    card_masked_number = serializers.SerializerMethodField()
    card_holder_name = serializers.ReadOnlyField(source='card.card_holder_name')

    class Meta:
        model = Transaction
        fields = (
            'id',
            'card',
            'card_masked_number',
            'card_holder_name',
            'transaction_type',
            'amount',
            'description',
            'status',
            'reference_number',
            'balance_before',
            'balance_after',
            'created_at',
            'updated_at'
        )
        read_only_fields = (
            'id',
            'reference_number',
            'status',
            'balance_before',
            'balance_after',
            'created_at',
            'updated_at'
        )

    def get_card_masked_number(self, obj):
        """Return masked card number"""
        return obj.card.masked_card_number

    def validate_amount(self, value):
        """Validate transaction amount"""
        if value <= 0:
            raise serializers.ValidationError(
                "Transaction amount must be greater than zero."
            )
        if value > Decimal('1000000.00'):
            raise serializers.ValidationError(
                "Transaction amount exceeds maximum limit."
            )
        return value

    def validate(self, attrs):
        """Validate transaction based on type and card status"""
        card = attrs.get('card')
        transaction_type = attrs.get('transaction_type')
        amount = attrs.get('amount')

        # Check if card belongs to the requesting user
        request = self.context.get('request')
        if request and card.user != request.user:
            raise serializers.ValidationError(
                {"card": "You can only create transactions for your own cards."}
            )

        # Check card status
        if card.status != 'ACTIVE':
            raise serializers.ValidationError(
                {"card": f"Card is {card.status.lower()}. Cannot process transaction."}
            )

        # Check if card is expired
        if card.is_expired:
            raise serializers.ValidationError(
                {"card": "Card has expired. Cannot process transaction."}
            )

        # For debit transactions, check sufficient balance
        if transaction_type == 'DEBIT' and card.balance < amount:
            raise serializers.ValidationError(
                {"amount": f"Insufficient balance. Available: {card.balance}"}
            )

        return attrs


class TransactionCreateSerializer(serializers.Serializer):
    """Serializer for creating transactions with processing logic"""
    card_id = serializers.IntegerField()
    transaction_type = serializers.ChoiceField(choices=['CREDIT', 'DEBIT'])
    amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    description = serializers.CharField(max_length=255)

    def validate_card_id(self, value):
        """Validate card exists and belongs to user"""
        request = self.context.get('request')
        try:
            card = VirtualCard.objects.get(id=value)
            if card.user != request.user:
                raise serializers.ValidationError(
                    "You can only create transactions for your own cards."
                )
            if card.status != 'ACTIVE':
                raise serializers.ValidationError(
                    f"Card is {card.status.lower()}. Cannot process transaction."
                )
            if card.is_expired:
                raise serializers.ValidationError(
                    "Card has expired. Cannot process transaction."
                )
        except VirtualCard.DoesNotExist:
            raise serializers.ValidationError("Card not found.")
        return value

    def validate(self, attrs):
        """Validate transaction can be processed"""
        card = VirtualCard.objects.get(id=attrs['card_id'])
        if attrs['transaction_type'] == 'DEBIT' and card.balance < attrs['amount']:
            raise serializers.ValidationError(
                {"amount": f"Insufficient balance. Available: {card.balance}"}
            )
        return attrs


class AccountSummarySerializer(serializers.ModelSerializer):
    """Serializer for account summary"""
    username = serializers.ReadOnlyField(source='user.username')
    email = serializers.ReadOnlyField(source='user.email')

    class Meta:
        model = AccountSummary
        fields = (
            'id',
            'username',
            'email',
            'total_balance',
            'total_cards',
            'active_cards',
            'total_transactions',
            'total_credited',
            'total_debited',
            'last_transaction_date',
            'updated_at'
        )
        read_only_fields = '__all__'
