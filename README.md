# Fintech Card Processing Platform

A full-stack virtual card management and transaction processing application built with Django REST Framework and React TypeScript.

## Features

### Backend (Django + DRF)
- **User Authentication**: JWT-based authentication with registration and login
- **Virtual Card Management**: Create, view, block/unblock virtual cards
- **Transaction Processing**: Credit and debit transactions with validation
- **Account Summary**: Aggregated financial data and statistics
- **Clean Architecture**: Following SOLID principles with separated business logic
- **API Documentation**: Interactive Swagger/ReDoc documentation
- **Rate Limiting**: Protection against API abuse
- **Comprehensive Testing**: Unit tests with pytest
- **Database**: PostgreSQL with proper relationships and migrations

### Frontend (React + TypeScript)
- **Authentication UI**: Login and registration forms
- **Dashboard**: Overview with account summary and key metrics
- **Card Management**: View cards, create new cards, block/unblock cards
- **Transaction Management**: Create transactions, view transaction history
- **Real-time Updates**: Automatic data refresh
- **Error Handling**: Graceful error handling with user notifications
- **Responsive Design**: Material-UI components for clean, modern interface

## Tech Stack

### Backend
- Python 3.11
- Django 4.2
- Django REST Framework 3.14
- PostgreSQL 15
- JWT Authentication (Simple JWT)
- Docker & Docker Compose
- Pytest for testing
- drf-yasg for API documentation

### Frontend
- React 18
- TypeScript
- Material-UI (MUI)
- Axios for API calls
- React Router for navigation
- Notistack for notifications

## Project Structure

```
Fintech Card Processing Platform/
├── backend/
│   ├── fintech_backend/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   ├── urls.py
│   │   ├── wsgi.py
│   │   └── asgi.py
│   ├── cards/
│   │   ├── models.py          # Data models
│   │   ├── serializers.py     # DRF serializers
│   │   ├── views.py           # API views
│   │   ├── services.py        # Business logic
│   │   ├── urls.py            # URL routing
│   │   ├── admin.py           # Admin interface
│   │   └── tests.py           # Unit tests
│   ├── manage.py
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── entrypoint.sh
│   └── pytest.ini
├── frontend/
│   ├── public/
│   │   └── index.html
│   ├── src/
│   │   ├── components/
│   │   │   ├── Login.tsx
│   │   │   ├── Register.tsx
│   │   │   ├── Dashboard.tsx
│   │   │   ├── CardList.tsx
│   │   │   ├── TransactionList.tsx
│   │   │   ├── CreateCardDialog.tsx
│   │   │   ├── CreateTransactionDialog.tsx
│   │   │   └── AccountSummaryCard.tsx
│   │   ├── services/
│   │   │   └── api.ts         # API service layer
│   │   ├── types/
│   │   │   └── index.ts       # TypeScript types
│   │   ├── App.tsx
│   │   └── index.tsx
│   ├── package.json
│   ├── tsconfig.json
│   ├── Dockerfile
│   └── nginx.conf
├── docker-compose.yml
├── .env
├── .gitignore
└── README.md
```

## Quick Start with Docker

### Prerequisites
- Docker Desktop installed
- Docker Compose installed

### Setup and Run

1. **Clone or navigate to the project directory**
   ```bash
   cd "Fintech Card Processing Platform"
   ```

2. **Start all services**
   ```bash
   docker-compose up --build
   ```

   This will start:
   - PostgreSQL database on port 5432
   - Django backend on http://localhost:8000
   - React frontend on http://localhost:3000

3. **Access the application**
   - Frontend: http://localhost:3000
   - Backend API: http://localhost:8000/api
   - API Documentation (Swagger): http://localhost:8000/swagger/
   - API Documentation (ReDoc): http://localhost:8000/redoc/
   - Django Admin: http://localhost:8000/admin

4. **Default Admin Credentials**
   - Username: `admin`
   - Password: `admin123`

### Stop Services
```bash
docker-compose down
```

### Stop Services and Remove Volumes
```bash
docker-compose down -v
```

## Local Development Setup (Without Docker)

### Backend Setup

1. **Create virtual environment**
   ```bash
   cd backend
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up PostgreSQL**
   - Install PostgreSQL
   - Create database: `fintech_db`
   - Update `.env` file with database credentials

4. **Run migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create superuser**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run development server**
   ```bash
   python manage.py runserver
   ```

7. **Run tests**
   ```bash
   pytest
   ```

### Frontend Setup

1. **Install dependencies**
   ```bash
   cd frontend
   npm install
   ```

2. **Create .env file**
   ```bash
   cp .env.example .env
   ```
   Update `REACT_APP_API_URL` if needed (default: http://localhost:8000/api)

3. **Start development server**
   ```bash
   npm start
   ```

4. **Build for production**
   ```bash
   npm run build
   ```

## API Endpoints

### Authentication
- `POST /api/auth/register/` - Register new user
- `POST /api/auth/login/` - Login and get JWT tokens
- `POST /api/auth/refresh/` - Refresh access token
- `GET /api/auth/me/` - Get current user details

### Cards
- `GET /api/cards/` - List all user's cards
- `POST /api/cards/` - Create new virtual card
- `GET /api/cards/{id}/` - Get card details
- `POST /api/cards/{id}/block/` - Block a card
- `POST /api/cards/{id}/unblock/` - Unblock a card
- `GET /api/cards/{id}/transactions/` - Get card transactions

### Transactions
- `GET /api/transactions/` - List all transactions
- `GET /api/transactions/{id}/` - Get transaction details
- `POST /api/transactions/process/` - Process new transaction

### Account
- `GET /api/account/summary/` - Get account summary

## Example API Calls

### 1. Register User
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "first_name": "John",
    "last_name": "Doe",
    "password": "securepassword123",
    "password2": "securepassword123"
  }'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "password": "securepassword123"
  }'
```

Response:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 3. Create Virtual Card
```bash
curl -X POST http://localhost:8000/api/cards/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "card_holder_name": "JOHN DOE",
    "initial_balance": "1000.00"
  }'
```

### 4. Process Transaction (Credit)
```bash
curl -X POST http://localhost:8000/api/transactions/process/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "card_id": 1,
    "transaction_type": "CREDIT",
    "amount": "500.00",
    "description": "Deposit funds"
  }'
```

### 5. Process Transaction (Debit)
```bash
curl -X POST http://localhost:8000/api/transactions/process/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "card_id": 1,
    "transaction_type": "DEBIT",
    "amount": "50.00",
    "description": "Purchase at Store"
  }'
```

### 6. Get Account Summary
```bash
curl -X GET http://localhost:8000/api/account/summary/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 7. Block Card
```bash
curl -X POST http://localhost:8000/api/cards/1/block/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Testing

### Run Backend Tests
```bash
cd backend
pytest
```

### Test Coverage
```bash
pytest --cov=cards --cov-report=html
```

## Database Schema

### User (Django Built-in)
- id, username, email, password, first_name, last_name

### VirtualCard
- id, user (FK), card_number, card_holder_name, expiry_date, cvv, balance, status, created_at, updated_at

### Transaction
- id, card (FK), transaction_type, amount, description, status, reference_number, balance_before, balance_after, created_at, updated_at

### AccountSummary
- id, user (FK), total_balance, total_cards, active_cards, total_transactions, total_credited, total_debited, last_transaction_date, updated_at

## Security Features

- JWT-based authentication with token refresh
- Password hashing with Django's built-in authentication
- CORS protection
- Rate limiting on API endpoints
- SQL injection protection through ORM
- XSS protection through React
- Database transaction atomicity for financial operations
- Card number masking in API responses

## Rate Limits

- Anonymous users: 100 requests/hour
- Authenticated users: 1000 requests/hour
- Transaction processing: 50 requests/hour

## Environment Variables

### Backend (.env)
```
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DB_NAME=fintech_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440
```

### Frontend (.env)
```
REACT_APP_API_URL=http://localhost:8000/api
```

## Production Deployment Notes

### Backend
1. Set `DEBUG=False` in production
2. Generate a strong `SECRET_KEY`
3. Update `ALLOWED_HOSTS` with your domain
4. Use environment-specific database credentials
5. Set up proper HTTPS/SSL
6. Configure static file serving (e.g., WhiteNoise or CDN)
7. Use production-grade WSGI server (Gunicorn is included)

### Frontend
1. Update `REACT_APP_API_URL` to production backend URL
2. Build optimized production bundle
3. Deploy static files to CDN or web server
4. Configure proper caching headers

### Database
1. Use managed PostgreSQL service (AWS RDS, Azure Database, etc.)
2. Set up regular backups
3. Configure connection pooling
4. Enable SSL connections

## Troubleshooting

### Docker Issues

**Database connection errors:**
```bash
docker-compose down -v
docker-compose up --build
```

**Port already in use:**
- Change port mappings in `docker-compose.yml`
- Or stop conflicting services

### Backend Issues

**Migration errors:**
```bash
python manage.py makemigrations
python manage.py migrate --run-syncdb
```

**Import errors:**
```bash
pip install -r requirements.txt
```

### Frontend Issues

**Module not found:**
```bash
rm -rf node_modules package-lock.json
npm install
```

**API connection errors:**
- Check `REACT_APP_API_URL` in `.env`
- Verify backend is running
- Check CORS settings

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

MIT License

## Support

For issues and questions:
- Open an issue on GitHub
- Check API documentation at `/swagger/`
- Review test files for usage examples

## Authors

Built with clean architecture principles and SOLID design patterns.
