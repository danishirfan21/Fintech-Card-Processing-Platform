#!/usr/bin/env python3
"""
API Testing Script for Fintech Card Processing Platform
This script demonstrates all major API endpoints
"""

import requests
import json
from typing import Optional

BASE_URL = "http://localhost:8000/api"


class FintechAPITester:
    def __init__(self):
        self.access_token: Optional[str] = None
        self.user_id: Optional[int] = None
        self.card_id: Optional[int] = None

    def print_response(self, title: str, response: requests.Response):
        """Print formatted API response"""
        print(f"\n{'=' * 60}")
        print(f"{title}")
        print(f"{'=' * 60}")
        print(f"Status Code: {response.status_code}")
        try:
            print(f"Response: {json.dumps(response.json(), indent=2)}")
        except:
            print(f"Response: {response.text}")

    def register_user(self, username: str = "testuser", email: str = "test@example.com"):
        """Register a new user"""
        url = f"{BASE_URL}/auth/register/"
        data = {
            "username": username,
            "email": email,
            "first_name": "Test",
            "last_name": "User",
            "password": "testpass123",
            "password2": "testpass123"
        }
        response = requests.post(url, json=data)
        self.print_response("1. REGISTER USER", response)
        return response.status_code == 201

    def login(self, username: str = "testuser", password: str = "testpass123"):
        """Login and get JWT token"""
        url = f"{BASE_URL}/auth/login/"
        data = {
            "username": username,
            "password": password
        }
        response = requests.post(url, json=data)
        self.print_response("2. LOGIN", response)

        if response.status_code == 200:
            self.access_token = response.json()["access"]
            return True
        return False

    def get_headers(self):
        """Get authorization headers"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }

    def get_current_user(self):
        """Get current user details"""
        url = f"{BASE_URL}/auth/me/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("3. GET CURRENT USER", response)

        if response.status_code == 200:
            self.user_id = response.json()["id"]
            return True
        return False

    def create_card(self, card_holder_name: str = "TEST USER", initial_balance: str = "1000.00"):
        """Create a virtual card"""
        url = f"{BASE_URL}/cards/"
        data = {
            "card_holder_name": card_holder_name,
            "initial_balance": initial_balance
        }
        response = requests.post(url, json=data, headers=self.get_headers())
        self.print_response("4. CREATE VIRTUAL CARD", response)

        if response.status_code == 201:
            self.card_id = response.json()["card"]["id"]
            return True
        return False

    def list_cards(self):
        """List all user's cards"""
        url = f"{BASE_URL}/cards/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("5. LIST CARDS", response)
        return response.status_code == 200

    def create_credit_transaction(self, amount: str = "500.00"):
        """Create a credit transaction"""
        url = f"{BASE_URL}/transactions/process/"
        data = {
            "card_id": self.card_id,
            "transaction_type": "CREDIT",
            "amount": amount,
            "description": "Test credit - Adding funds"
        }
        response = requests.post(url, json=data, headers=self.get_headers())
        self.print_response("6. PROCESS CREDIT TRANSACTION", response)
        return response.status_code == 201

    def create_debit_transaction(self, amount: str = "100.00"):
        """Create a debit transaction"""
        url = f"{BASE_URL}/transactions/process/"
        data = {
            "card_id": self.card_id,
            "transaction_type": "DEBIT",
            "amount": amount,
            "description": "Test debit - Purchase at store"
        }
        response = requests.post(url, json=data, headers=self.get_headers())
        self.print_response("7. PROCESS DEBIT TRANSACTION", response)
        return response.status_code == 201

    def list_transactions(self):
        """List all transactions"""
        url = f"{BASE_URL}/transactions/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("8. LIST TRANSACTIONS", response)
        return response.status_code == 200

    def get_account_summary(self):
        """Get account summary"""
        url = f"{BASE_URL}/account/summary/"
        response = requests.get(url, headers=self.get_headers())
        self.print_response("9. GET ACCOUNT SUMMARY", response)
        return response.status_code == 200

    def block_card(self):
        """Block a card"""
        url = f"{BASE_URL}/cards/{self.card_id}/block/"
        response = requests.post(url, headers=self.get_headers())
        self.print_response("10. BLOCK CARD", response)
        return response.status_code == 200

    def unblock_card(self):
        """Unblock a card"""
        url = f"{BASE_URL}/cards/{self.card_id}/unblock/"
        response = requests.post(url, headers=self.get_headers())
        self.print_response("11. UNBLOCK CARD", response)
        return response.status_code == 200

    def run_all_tests(self):
        """Run all API tests"""
        print("\n" + "=" * 60)
        print("FINTECH CARD PROCESSING PLATFORM - API TEST")
        print("=" * 60)

        # Test flow
        success = True

        # Register (might fail if user exists, that's ok)
        self.register_user()

        # Login
        if not self.login():
            print("\n❌ Login failed. Cannot continue tests.")
            return

        # Get user info
        if not self.get_current_user():
            print("\n❌ Failed to get user info.")
            return

        # Create card
        if not self.create_card():
            print("\n❌ Failed to create card.")
            return

        # List cards
        self.list_cards()

        # Credit transaction
        self.create_credit_transaction()

        # Debit transaction
        self.create_debit_transaction()

        # List transactions
        self.list_transactions()

        # Get account summary
        self.get_account_summary()

        # Block card
        self.block_card()

        # Unblock card
        self.unblock_card()

        print("\n" + "=" * 60)
        print("✓ ALL TESTS COMPLETED")
        print("=" * 60)
        print("\nCheck the responses above to verify all endpoints are working correctly.")
        print("You can now test the frontend at http://localhost:3000")
        print("Or explore the API docs at http://localhost:8000/swagger/")


def main():
    """Main function"""
    tester = FintechAPITester()
    try:
        tester.run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ Error: Cannot connect to the API.")
        print("Please make sure the backend is running on http://localhost:8000")
        print("Run: docker-compose up")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()
