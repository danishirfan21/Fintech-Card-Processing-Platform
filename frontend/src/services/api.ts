/**
 * API Service Layer
 * Handles all HTTP requests to the backend API
 */
import axios, { AxiosError, AxiosInstance } from 'axios';
import {
  User,
  AuthTokens,
  LoginCredentials,
  RegisterData,
  VirtualCard,
  CardCreateData,
  Transaction,
  TransactionCreateData,
  AccountSummary,
  PaginatedResponse,
  ApiError,
} from '../types';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000/api';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add request interceptor to include auth token
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Add response interceptor to handle token refresh
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        const originalRequest: any = error.config;

        // If error is 401 and we haven't retried yet
        if (error.response?.status === 401 && !originalRequest._retry) {
          originalRequest._retry = true;

          try {
            const refreshToken = localStorage.getItem('refresh_token');
            if (refreshToken) {
              const response = await axios.post(`${API_URL}/auth/refresh/`, {
                refresh: refreshToken,
              });

              const { access } = response.data;
              localStorage.setItem('access_token', access);

              // Retry original request with new token
              originalRequest.headers.Authorization = `Bearer ${access}`;
              return this.api(originalRequest);
            }
          } catch (refreshError) {
            // Refresh failed, logout user
            localStorage.removeItem('access_token');
            localStorage.removeItem('refresh_token');
            window.location.href = '/login';
            return Promise.reject(refreshError);
          }
        }

        return Promise.reject(error);
      }
    );
  }

  // Authentication endpoints

  async register(data: RegisterData): Promise<{ message: string; user: User }> {
    const response = await this.api.post('/auth/register/', data);
    return response.data;
  }

  async login(credentials: LoginCredentials): Promise<AuthTokens> {
    const response = await this.api.post('/auth/login/', credentials);
    const { access, refresh } = response.data;

    // Store tokens
    localStorage.setItem('access_token', access);
    localStorage.setItem('refresh_token', refresh);

    return response.data;
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  async getCurrentUser(): Promise<User> {
    const response = await this.api.get('/auth/me/');
    return response.data;
  }

  // Card endpoints

  async getCards(): Promise<PaginatedResponse<VirtualCard>> {
    const response = await this.api.get('/cards/');
    return response.data;
  }

  async getCard(id: number): Promise<VirtualCard> {
    const response = await this.api.get(`/cards/${id}/`);
    return response.data;
  }

  async createCard(data: CardCreateData): Promise<{ message: string; card: VirtualCard }> {
    const response = await this.api.post('/cards/', data);
    return response.data;
  }

  async blockCard(id: number): Promise<{ message: string; card: VirtualCard }> {
    const response = await this.api.post(`/cards/${id}/block/`);
    return response.data;
  }

  async unblockCard(id: number): Promise<{ message: string; card: VirtualCard }> {
    const response = await this.api.post(`/cards/${id}/unblock/`);
    return response.data;
  }

  async getCardTransactions(cardId: number): Promise<Transaction[]> {
    const response = await this.api.get(`/cards/${cardId}/transactions/`);
    return response.data;
  }

  // Transaction endpoints

  async getTransactions(params?: {
    status?: string;
    type?: string;
  }): Promise<PaginatedResponse<Transaction>> {
    const response = await this.api.get('/transactions/', { params });
    return response.data;
  }

  async getTransaction(id: number): Promise<Transaction> {
    const response = await this.api.get(`/transactions/${id}/`);
    return response.data;
  }

  async processTransaction(
    data: TransactionCreateData
  ): Promise<{ message: string; transaction: Transaction }> {
    const response = await this.api.post('/transactions/process/', data);
    return response.data;
  }

  // Account endpoints

  async getAccountSummary(): Promise<AccountSummary> {
    const response = await this.api.get('/account/summary/');
    return response.data;
  }

  // Error handler utility
  handleError(error: unknown): string {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError<ApiError>;

      if (axiosError.response?.data) {
        const errorData = axiosError.response.data;

        // Handle different error formats
        if (errorData.error) {
          return errorData.error;
        }

        if (errorData.detail) {
          return errorData.detail;
        }

        // Handle validation errors
        const firstKey = Object.keys(errorData)[0];
        if (firstKey && Array.isArray(errorData[firstKey])) {
          return errorData[firstKey][0];
        }

        if (firstKey) {
          return `${firstKey}: ${errorData[firstKey]}`;
        }
      }

      if (axiosError.message) {
        return axiosError.message;
      }
    }

    return 'An unexpected error occurred';
  }
}

export default new ApiService();
