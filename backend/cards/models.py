"""
Models for the Fintech Card Processing Platform.
Following clean architecture and SOLID principles.
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
import random
import string
from datetime import datetime, timedelta


class VirtualCard(models.Model):
    """
    Virtual Card model representing a user's virtual payment card.
    """
    CARD_STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('BLOCKED', 'Blocked'),
        ('EXPIRED', 'Expired'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='cards'
    )
    card_number = models.CharField(
        max_length=16,
        unique=True,
        editable=False
    )
    card_holder_name = models.CharField(max_length=100)
    expiry_date = models.DateField()
    cvv = models.CharField(max_length=3, editable=False)
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    status = models.CharField(
        max_length=10,
        choices=CARD_STATUS_CHOICES,
        default='ACTIVE'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['card_number']),
        ]

    def __str__(self):
        return f"{self.card_holder_name} - {self.masked_card_number}"

    @property
    def masked_card_number(self):
        """Return masked card number (XXXX-XXXX-XXXX-1234)"""
        return f"XXXX-XXXX-XXXX-{self.card_number[-4:]}"

    @property
    def is_expired(self):
        """Check if card is expired"""
        return self.expiry_date < datetime.now().date()

    def save(self, *args, **kwargs):
        """Override save to generate card number and CVV"""
        if not self.card_number:
            self.card_number = self._generate_card_number()
        if not self.cvv:
            self.cvv = self._generate_cvv()
        if not self.expiry_date:
            # Default expiry: 3 years from now
            self.expiry_date = (datetime.now() + timedelta(days=365*3)).date()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_card_number():
        """Generate a unique 16-digit card number"""
        while True:
            card_number = ''.join([str(random.randint(0, 9)) for _ in range(16)])
            if not VirtualCard.objects.filter(card_number=card_number).exists():
                return card_number

    @staticmethod
    def _generate_cvv():
        """Generate a 3-digit CVV"""
        return ''.join([str(random.randint(0, 9)) for _ in range(3)])


class Transaction(models.Model):
    """
    Transaction model for tracking card transactions.
    """
    TRANSACTION_TYPE_CHOICES = [
        ('CREDIT', 'Credit'),
        ('DEBIT', 'Debit'),
    ]

    TRANSACTION_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('COMPLETED', 'Completed'),
        ('FAILED', 'Failed'),
        ('REVERSED', 'Reversed'),
    ]

    card = models.ForeignKey(
        VirtualCard,
        on_delete=models.CASCADE,
        related_name='transactions'
    )
    transaction_type = models.CharField(
        max_length=6,
        choices=TRANSACTION_TYPE_CHOICES
    )
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    description = models.CharField(max_length=255)
    status = models.CharField(
        max_length=10,
        choices=TRANSACTION_STATUS_CHOICES,
        default='PENDING'
    )
    reference_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False
    )
    balance_before = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    balance_after = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['card', 'status']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.reference_number}"

    def save(self, *args, **kwargs):
        """Override save to generate reference number"""
        if not self.reference_number:
            self.reference_number = self._generate_reference_number()
        super().save(*args, **kwargs)

    @staticmethod
    def _generate_reference_number():
        """Generate a unique transaction reference number"""
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        return f"TXN{timestamp}{random_str}"


class AccountSummary(models.Model):
    """
    Account Summary model for aggregated user financial data.
    This provides a cached view of user's account information.
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='account_summary'
    )
    total_balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_cards = models.IntegerField(default=0)
    active_cards = models.IntegerField(default=0)
    total_transactions = models.IntegerField(default=0)
    total_credited = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    total_debited = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    last_transaction_date = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Account Summaries"

    def __str__(self):
        return f"Account Summary - {self.user.username}"

    def update_summary(self):
        """Update account summary with latest data"""
        cards = self.user.cards.all()
        self.total_cards = cards.count()
        self.active_cards = cards.filter(status='ACTIVE').count()
        self.total_balance = sum(card.balance for card in cards)

        transactions = Transaction.objects.filter(
            card__user=self.user,
            status='COMPLETED'
        )
        self.total_transactions = transactions.count()
        self.total_credited = sum(
            t.amount for t in transactions.filter(transaction_type='CREDIT')
        ) or Decimal('0.00')
        self.total_debited = sum(
            t.amount for t in transactions.filter(transaction_type='DEBIT')
        ) or Decimal('0.00')

        last_transaction = transactions.first()
        if last_transaction:
            self.last_transaction_date = last_transaction.created_at

        self.save()
