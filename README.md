# ALX Travel App

## Payment Integration with Chapa

This project implements payment functionality using the Chapa payment gateway.

### Features Implemented

1. **Payment Model**: Stores payment information including booking reference, payment status, amount, and transaction ID
2. **Payment API Endpoints**:
   - `POST /api/payments/initiate/` - Initiates payment process
   - `GET /api/payments/verify/` - Verifies payment status
3. **Celery Integration**: Background task for sending confirmation emails
4. **Environment Variables**: Secure storage of Chapa API keys

### Setup Instructions

1. Create a `.env` file in the project root with:
   ```
   DEBUG=True
   SECRET_KEY=your-secret-key-here
   CHAPA_SECRET_KEY=your-chapa-secret-key-here
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run migrations:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

4. Start Redis server (required for Celery):
   ```bash
   redis-server
   ```

5. Start Celery worker:
   ```bash
   celery -A alx_travel_app worker --loglevel=info
   ```

6. Run the Django development server:
   ```bash
   python manage.py runserver
   ```

### API Endpoints

- **Initiate Payment**: `POST /api/payments/initiate/`
  - Request body: `{"booking_id": "uuid-string"}`
  - Response: `{"payment_id": "uuid-string", "checkout_url": "url"}`

- **Verify Payment**: `GET /api/payments/verify/?tx_ref=payment_id`
  - Response: `{"message": "Payment verified successfully", "payment_status": "completed"}`

### Testing

To test with Chapa's sandbox environment:
1. Create an account at https://developer.chapa.co/
2. Use the sandbox API keys in your `.env` file
3. Test the payment flow through the API endpoints
