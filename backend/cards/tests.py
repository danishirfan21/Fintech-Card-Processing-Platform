"""
Comprehensive unit tests for the Fintech Card Processing Platform.
Tests cover models, services, and API endpoints.
"""
import pytest
from decimal import Decimal
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from rest_framework.test import APIClient
from rest_framework import status
from datetime import datetime, timedelta

from .models import VirtualCard, Transaction, AccountSummary
from .services import TransactionService, CardService


# Fixtures

@pytest.fixture
def api_client():
    """Create an API client for testing"""
    return APIClient()


@pytest.fixture
@pytest.mark.django_db
def test_user():
    """Create a test user"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )
    return user


@pytest.fixture
@pytest.mark.django_db
def test_card(test_user):
    """Create a test virtual card"""
    card = VirtualCard.objects.create(
        user=test_user,
        card_holder_name='TEST USER',
        balance=Decimal('1000.00')
    )
    return card


@pytest.fixture
@pytest.mark.django_db
def authenticated_client(api_client, test_user):
    """Create an authenticated API client"""
    api_client.force_authenticate(user=test_user)
    return api_client


# Model Tests

@pytest.mark.django_db
class TestVirtualCardModel:
    """Test VirtualCard model functionality"""

    def test_card_creation(self, test_user):
        """Test that a card is created with auto-generated fields"""
        card = VirtualCard.objects.create(
            user=test_user,
            card_holder_name='JOHN DOE',
            balance=Decimal('500.00')
        )

        assert card.card_number is not None
        assert len(card.card_number) == 16
        assert card.cvv is not None
        assert len(card.cvv) == 3
        assert card.expiry_date is not None
        assert card.status == 'ACTIVE'
        assert card.balance == Decimal('500.00')

    def test_card_number_uniqueness(self, test_user):
        """Test that card numbers are unique"""
        card1 = VirtualCard.objects.create(
            user=test_user,
            card_holder_name='USER ONE'
        )
        card2 = VirtualCard.objects.create(
            user=test_user,
            card_holder_name='USER TWO'
        )

        assert card1.card_number != card2.card_number

    def test_masked_card_number(self, test_card):
        """Test masked card number property"""
        masked = test_card.masked_card_number
        assert masked.startswith('XXXX-XXXX-XXXX-')
        assert masked.endswith(test_card.card_number[-4:])

    def test_is_expired_property(self, test_user):
        """Test card expiry check"""
        # Create expired card
        expired_card = VirtualCard.objects.create(
            user=test_user,
            card_holder_name='EXPIRED USER'
        )
        expired_card.expiry_date = datetime.now().date() - timedelta(days=1)
        expired_card.save()

        assert expired_card.is_expired is True

        # Create active card
        active_card = VirtualCard.objects.create(
            user=test_user,
            card_holder_name='ACTIVE USER'
        )
        assert active_card.is_expired is False


@pytest.mark.django_db
class TestTransactionModel:
    """Test Transaction model functionality"""

    def test_transaction_creation(self, test_card):
        """Test transaction creation with auto-generated reference"""
        transaction = Transaction.objects.create(
            card=test_card,
            transaction_type='CREDIT',
            amount=Decimal('100.00'),
            description='Test credit',
            status='COMPLETED'
        )

        assert transaction.reference_number is not None
        assert transaction.reference_number.startswith('TXN')
        assert transaction.amount == Decimal('100.00')
        assert transaction.status == 'COMPLETED'

    def test_reference_number_uniqueness(self, test_card):
        """Test that transaction reference numbers are unique"""
        txn1 = Transaction.objects.create(
            card=test_card,
            transaction_type='CREDIT',
            amount=Decimal('50.00'),
            description='Transaction 1'
        )
        txn2 = Transaction.objects.create(
            card=test_card,
            transaction_type='DEBIT',
            amount=Decimal('25.00'),
            description='Transaction 2'
        )

        assert txn1.reference_number != txn2.reference_number


# Service Tests

@pytest.mark.django_db
class TestTransactionService:
    """Test TransactionService business logic"""

    def test_credit_transaction(self, test_card):
        """Test successful credit transaction"""
        initial_balance = test_card.balance
        amount = Decimal('500.00')

        transaction = TransactionService.process_transaction(
            card_id=test_card.id,
            transaction_type='CREDIT',
            amount=amount,
            description='Test credit'
        )

        test_card.refresh_from_db()

        assert transaction.status == 'COMPLETED'
        assert transaction.balance_before == initial_balance
        assert transaction.balance_after == initial_balance + amount
        assert test_card.balance == initial_balance + amount

    def test_debit_transaction_success(self, test_card):
        """Test successful debit transaction"""
        initial_balance = test_card.balance
        amount = Decimal('200.00')

        transaction = TransactionService.process_transaction(
            card_id=test_card.id,
            transaction_type='DEBIT',
            amount=amount,
            description='Test debit'
        )

        test_card.refresh_from_db()

        assert transaction.status == 'COMPLETED'
        assert transaction.balance_before == initial_balance
        assert transaction.balance_after == initial_balance - amount
        assert test_card.balance == initial_balance - amount

    def test_debit_transaction_insufficient_balance(self, test_card):
        """Test debit transaction with insufficient balance"""
        initial_balance = test_card.balance
        amount = Decimal('2000.00')  # More than balance

        with pytest.raises(ValidationError, match='Insufficient balance'):
            TransactionService.process_transaction(
                card_id=test_card.id,
                transaction_type='DEBIT',
                amount=amount,
                description='Test insufficient funds'
            )

        test_card.refresh_from_db()
        assert test_card.balance == initial_balance  # Balance unchanged

    def test_transaction_on_blocked_card(self, test_card):
        """Test transaction on blocked card fails"""
        test_card.status = 'BLOCKED'
        test_card.save()

        with pytest.raises(ValidationError, match='blocked'):
            TransactionService.process_transaction(
                card_id=test_card.id,
                transaction_type='CREDIT',
                amount=Decimal('100.00'),
                description='Test blocked card'
            )

    def test_transaction_on_expired_card(self, test_card):
        """Test transaction on expired card fails"""
        test_card.expiry_date = datetime.now().date() - timedelta(days=1)
        test_card.save()

        with pytest.raises(ValidationError, match='expired'):
            TransactionService.process_transaction(
                card_id=test_card.id,
                transaction_type='CREDIT',
                amount=Decimal('100.00'),
                description='Test expired card'
            )


@pytest.mark.django_db
class TestCardService:
    """Test CardService business logic"""

    def test_create_card(self, test_user):
        """Test card creation through service"""
        card = CardService.create_card(
            user=test_user,
            card_holder_name='john doe',
            initial_balance=Decimal('250.00')
        )

        assert card.card_holder_name == 'JOHN DOE'  # Should be uppercase
        assert card.balance == Decimal('250.00')
        assert card.status == 'ACTIVE'

    def test_block_card(self, test_card):
        """Test blocking a card"""
        card = CardService.block_card(test_card.id, test_card.user)

        assert card.status == 'BLOCKED'

    def test_unblock_card(self, test_card):
        """Test unblocking a card"""
        test_card.status = 'BLOCKED'
        test_card.save()

        card = CardService.unblock_card(test_card.id, test_card.user)

        assert card.status == 'ACTIVE'

    def test_cannot_unblock_expired_card(self, test_card):
        """Test that expired cards cannot be unblocked"""
        test_card.status = 'BLOCKED'
        test_card.expiry_date = datetime.now().date() - timedelta(days=1)
        test_card.save()

        with pytest.raises(ValidationError, match='expired'):
            CardService.unblock_card(test_card.id, test_card.user)


# API Tests

@pytest.mark.django_db
class TestAuthenticationAPI:
    """Test authentication endpoints"""

    def test_user_registration(self, api_client):
        """Test user registration endpoint"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'first_name': 'New',
            'last_name': 'User',
            'password': 'strongpass123',
            'password2': 'strongpass123'
        }

        response = api_client.post('/api/auth/register/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'user' in response.data
        assert response.data['user']['username'] == 'newuser'
        assert User.objects.filter(username='newuser').exists()

    def test_user_registration_password_mismatch(self, api_client):
        """Test registration with password mismatch"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'password123',
            'password2': 'different123'
        }

        response = api_client.post('/api/auth/register/', data)

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_user_login(self, api_client, test_user):
        """Test user login endpoint"""
        data = {
            'username': 'testuser',
            'password': 'testpass123'
        }

        response = api_client.post('/api/auth/login/', data)

        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data


@pytest.mark.django_db
class TestVirtualCardAPI:
    """Test virtual card API endpoints"""

    def test_create_card(self, authenticated_client):
        """Test creating a virtual card"""
        data = {
            'card_holder_name': 'Jane Doe',
            'initial_balance': '500.00'
        }

        response = authenticated_client.post('/api/cards/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'card' in response.data
        assert response.data['card']['card_holder_name'] == 'JANE DOE'
        assert Decimal(response.data['card']['balance']) == Decimal('500.00')

    def test_list_cards(self, authenticated_client, test_card):
        """Test listing user's cards"""
        response = authenticated_client.get('/api/cards/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1

    def test_retrieve_card(self, authenticated_client, test_card):
        """Test retrieving a specific card"""
        response = authenticated_client.get(f'/api/cards/{test_card.id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['id'] == test_card.id

    def test_block_card(self, authenticated_client, test_card):
        """Test blocking a card"""
        response = authenticated_client.post(f'/api/cards/{test_card.id}/block/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['card']['status'] == 'BLOCKED'

    def test_unblock_card(self, authenticated_client, test_card):
        """Test unblocking a card"""
        test_card.status = 'BLOCKED'
        test_card.save()

        response = authenticated_client.post(f'/api/cards/{test_card.id}/unblock/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['card']['status'] == 'ACTIVE'


@pytest.mark.django_db
class TestTransactionAPI:
    """Test transaction API endpoints"""

    def test_process_credit_transaction(self, authenticated_client, test_card):
        """Test processing a credit transaction"""
        data = {
            'card_id': test_card.id,
            'transaction_type': 'CREDIT',
            'amount': '250.00',
            'description': 'Test credit transaction'
        }

        response = authenticated_client.post('/api/transactions/process/', data)

        assert response.status_code == status.HTTP_201_CREATED
        assert 'transaction' in response.data
        assert response.data['transaction']['transaction_type'] == 'CREDIT'

    def test_process_debit_transaction(self, authenticated_client, test_card):
        """Test processing a debit transaction"""
        data = {
            'card_id': test_card.id,
            'transaction_type': 'DEBIT',
            'amount': '100.00',
            'description': 'Test debit transaction'
        }

        response = authenticated_client.post('/api/transactions/process/', data)

        assert response.status_code == status.HTTP_201_CREATED

    def test_list_transactions(self, authenticated_client, test_card):
        """Test listing transactions"""
        # Create a transaction first
        Transaction.objects.create(
            card=test_card,
            transaction_type='CREDIT',
            amount=Decimal('100.00'),
            description='Test transaction',
            status='COMPLETED'
        )

        response = authenticated_client.get('/api/transactions/')

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) >= 1


@pytest.mark.django_db
class TestAccountSummaryAPI:
    """Test account summary API"""

    def test_get_account_summary(self, authenticated_client, test_user, test_card):
        """Test retrieving account summary"""
        response = authenticated_client.get('/api/account/summary/')

        assert response.status_code == status.HTTP_200_OK
        assert 'total_balance' in response.data
        assert 'total_cards' in response.data
        assert Decimal(response.data['total_balance']) >= Decimal('0.00')
