/**
 * TypeScript type definitions for the Fintech Card Platform
 */

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  date_joined: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface RegisterData {
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  password: string;
  password2: string;
}

export interface VirtualCard {
  id: number;
  user: number;
  user_username: string;
  card_number?: string;
  masked_card_number: string;
  card_holder_name: string;
  expiry_date: string;
  cvv?: string;
  balance: string;
  status: 'ACTIVE' | 'BLOCKED' | 'EXPIRED';
  is_expired: boolean;
  created_at: string;
  updated_at: string;
}

export interface CardCreateData {
  card_holder_name: string;
  initial_balance?: string;
}

export interface Transaction {
  id: number;
  card: number;
  card_masked_number: string;
  card_holder_name: string;
  transaction_type: 'CREDIT' | 'DEBIT';
  amount: string;
  description: string;
  status: 'PENDING' | 'COMPLETED' | 'FAILED' | 'REVERSED';
  reference_number: string;
  balance_before: string | null;
  balance_after: string | null;
  created_at: string;
  updated_at: string;
}

export interface TransactionCreateData {
  card_id: number;
  transaction_type: 'CREDIT' | 'DEBIT';
  amount: string;
  description: string;
}

export interface AccountSummary {
  id: number;
  username: string;
  email: string;
  total_balance: string;
  total_cards: number;
  active_cards: number;
  total_transactions: number;
  total_credited: string;
  total_debited: string;
  last_transaction_date: string | null;
  updated_at: string;
}

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiError {
  error?: string;
  detail?: string;
  [key: string]: any;
}
