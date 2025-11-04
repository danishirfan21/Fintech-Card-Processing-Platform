"""
Business logic services for the Fintech Card Processing Platform.
Following clean architecture principles - separating business logic from views.
"""
from django.db import transaction
from django.core.exceptions import ValidationError
from decimal import Decimal
from .models import VirtualCard, Transaction, AccountSummary


class TransactionService:
    """
    Service class for processing transactions.
    Implements Single Responsibility Principle - handles only transaction processing.
    """

    @staticmethod
    @transaction.atomic
    def process_transaction(card_id, transaction_type, amount, description):
        """
        Process a transaction (credit or debit) for a card.

        Args:
            card_id: ID of the virtual card
            transaction_type: 'CREDIT' or 'DEBIT'
            amount: Transaction amount
            description: Transaction description

        Returns:
            Transaction object

        Raises:
            ValidationError: If transaction cannot be processed
        """
        try:
            # Lock the card row to prevent race conditions
            card = VirtualCard.objects.select_for_update().get(id=card_id)
        except VirtualCard.DoesNotExist:
            raise ValidationError("Card not found")

        # Validate card status
        if card.status != 'ACTIVE':
            raise ValidationError(f"Card is {card.status.lower()}. Cannot process transaction.")

        if card.is_expired:
            raise ValidationError("Card has expired. Cannot process transaction.")

        # Store balance before transaction
        balance_before = card.balance

        # Process based on transaction type
        if transaction_type == 'DEBIT':
            if card.balance < amount:
                # Create failed transaction record
                txn = Transaction.objects.create(
                    card=card,
                    transaction_type=transaction_type,
                    amount=amount,
                    description=description,
                    status='FAILED',
                    balance_before=balance_before,
                    balance_after=balance_before
                )
                raise ValidationError(f"Insufficient balance. Available: {card.balance}")

            card.balance -= amount

        elif transaction_type == 'CREDIT':
            card.balance += amount

        else:
            raise ValidationError("Invalid transaction type")

        # Save updated card balance
        card.save()

        # Create transaction record
        txn = Transaction.objects.create(
            card=card,
            transaction_type=transaction_type,
            amount=amount,
            description=description,
            status='COMPLETED',
            balance_before=balance_before,
            balance_after=card.balance
        )

        # Update account summary
        TransactionService._update_account_summary(card.user)

        return txn

    @staticmethod
    def _update_account_summary(user):
        """Update user's account summary after transaction"""
        summary, _ = AccountSummary.objects.get_or_create(user=user)
        summary.update_summary()


class CardService:
    """
    Service class for card operations.
    Implements Single Responsibility Principle - handles only card operations.
    """

    @staticmethod
    def create_card(user, card_holder_name, initial_balance=Decimal('0.00')):
        """
        Create a new virtual card for a user.

        Args:
            user: User object
            card_holder_name: Name on the card
            initial_balance: Initial card balance (default: 0.00)

        Returns:
            VirtualCard object
        """
        card = VirtualCard.objects.create(
            user=user,
            card_holder_name=card_holder_name.upper(),
            balance=initial_balance
        )

        # Update account summary
        summary, _ = AccountSummary.objects.get_or_create(user=user)
        summary.update_summary()

        return card

    @staticmethod
    def block_card(card_id, user):
        """
        Block a virtual card.

        Args:
            card_id: ID of the card to block
            user: User who owns the card

        Returns:
            VirtualCard object

        Raises:
            ValidationError: If card cannot be blocked
        """
        try:
            card = VirtualCard.objects.get(id=card_id, user=user)
        except VirtualCard.DoesNotExist:
            raise ValidationError("Card not found")

        if card.status == 'EXPIRED':
            raise ValidationError("Cannot block an expired card")

        card.status = 'BLOCKED'
        card.save()

        # Update account summary
        summary, _ = AccountSummary.objects.get_or_create(user=user)
        summary.update_summary()

        return card

    @staticmethod
    def unblock_card(card_id, user):
        """
        Unblock a virtual card.

        Args:
            card_id: ID of the card to unblock
            user: User who owns the card

        Returns:
            VirtualCard object

        Raises:
            ValidationError: If card cannot be unblocked
        """
        try:
            card = VirtualCard.objects.get(id=card_id, user=user)
        except VirtualCard.DoesNotExist:
            raise ValidationError("Card not found")

        if card.status != 'BLOCKED':
            raise ValidationError("Only blocked cards can be unblocked")

        if card.is_expired:
            raise ValidationError("Cannot unblock an expired card")

        card.status = 'ACTIVE'
        card.save()

        # Update account summary
        summary, _ = AccountSummary.objects.get_or_create(user=user)
        summary.update_summary()

        return card

    @staticmethod
    def get_user_cards(user, status=None):
        """
        Get all cards for a user, optionally filtered by status.

        Args:
            user: User object
            status: Optional status filter

        Returns:
            QuerySet of VirtualCard objects
        """
        cards = VirtualCard.objects.filter(user=user)
        if status:
            cards = cards.filter(status=status)
        return cards

    @staticmethod
    def get_card_transactions(card_id, user, status=None):
        """
        Get all transactions for a card.

        Args:
            card_id: ID of the card
            user: User who owns the card
            status: Optional status filter

        Returns:
            QuerySet of Transaction objects

        Raises:
            ValidationError: If card not found or doesn't belong to user
        """
        try:
            card = VirtualCard.objects.get(id=card_id, user=user)
        except VirtualCard.DoesNotExist:
            raise ValidationError("Card not found")

        transactions = Transaction.objects.filter(card=card)
        if status:
            transactions = transactions.filter(status=status)
        return transactions
