# Quick Start Guide

## Get Started in 3 Steps

### 1. Start the Application
```bash
docker-compose up --build
```

Wait for all services to start (about 2-3 minutes on first run).

### 2. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **API Documentation**: http://localhost:8000/swagger/

### 3. Create an Account
1. Open http://localhost:3000
2. Click "Sign Up"
3. Fill in the registration form
4. Login with your credentials

## First Steps After Login

### Create Your First Card
1. Click "Create Card" button
2. Enter cardholder name (e.g., "JOHN DOE")
3. Set initial balance (e.g., "1000.00")
4. Click "Create Card"

### Make a Transaction
1. Click "New Transaction" button
2. Select your card
3. Choose transaction type:
   - **Credit**: Add money to card
   - **Debit**: Spend money from card
4. Enter amount and description
5. Click "Process Transaction"

### View Your Dashboard
- **Account Summary**: Total balance, active cards, transaction counts
- **Card List**: All your cards with balances and status
- **Transaction History**: Recent transactions with details

## Testing the API

### Using Swagger UI
1. Go to http://localhost:8000/swagger/
2. Click "Authorize" button
3. Login to get JWT token
4. Paste token in format: `Bearer YOUR_TOKEN`
5. Test any endpoint

### Using cURL

**Register:**
```bash
curl -X POST http://localhost:8000/api/auth/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"testpass123","password2":"testpass123"}'
```

**Login:**
```bash
curl -X POST http://localhost:8000/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","password":"testpass123"}'
```

**Create Card (replace TOKEN):**
```bash
curl -X POST http://localhost:8000/api/cards/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"card_holder_name":"TEST USER","initial_balance":"500.00"}'
```

## Admin Panel

Access Django admin at http://localhost:8000/admin

**Default credentials:**
- Username: `admin`
- Password: `admin123`

## Stopping the Application

```bash
docker-compose down
```

## Troubleshooting

**Port already in use?**
```bash
# Stop conflicting services or edit docker-compose.yml to change ports
```

**Database issues?**
```bash
docker-compose down -v
docker-compose up --build
```

**Frontend not connecting to backend?**
- Check `REACT_APP_API_URL` in frontend/.env
- Ensure backend is running on port 8000

## Next Steps

- Read full [README.md](README.md) for detailed documentation
- Check [API Documentation](http://localhost:8000/swagger/) for all endpoints
- Run backend tests: `cd backend && pytest`
- Customize the application for your needs

## Support

- API Docs: http://localhost:8000/swagger/
- ReDoc: http://localhost:8000/redoc/
- GitHub Issues: [Report issues here]

Enjoy building with Fintech Card Platform!
