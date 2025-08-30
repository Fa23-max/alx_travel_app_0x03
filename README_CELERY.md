# Celery Configuration Guide

## Overview
This project is now configured with Celery for background task processing using RabbitMQ as the message broker.

## Prerequisites
1. **RabbitMQ Server**: Install and run RabbitMQ on your system
   - Windows: Download from https://www.rabbitmq.com/install-windows.html
   - Or use Docker: `docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management`

2. **Python Dependencies**: Install required packages
   ```bash
   pip install celery kombu
   ```

## Configuration Files

### 1. `alx_travel_app/celery.py`
- Main Celery application configuration
- Auto-discovers tasks from Django apps

### 2. `settings.py` - Celery Settings
```python
CELERY_BROKER_URL = 'amqp://guest@localhost//'
CELERY_RESULT_BACKEND = 'rpc://'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'
```

### 3. `listings/tasks.py` - Background Tasks
- `send_booking_confirmation_email`: Sends email when booking is created
- `send_payment_confirmation_email`: Sends email when payment is confirmed

## Email Configuration
Add these environment variables to your `.env` file:
```
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@alxtravel.com
```

## Running Celery

### 1. Start RabbitMQ Server
```bash
# If installed locally
rabbitmq-server

# Or using Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
```

### 2. Start Celery Worker
```bash
cd alx_travel_app
celery -A alx_travel_app worker --loglevel=info
```

### 3. Start Django Development Server
```bash
python manage.py runserver
```

## Testing

### 1. Run Test Script
```bash
python test_celery.py
```

### 2. Create a Booking via API
When you create a booking through the API, it will automatically trigger a background email task.

### 3. Monitor Tasks
- RabbitMQ Management UI: http://localhost:15672 (guest/guest)
- Check Celery worker logs for task execution

## Task Flow

1. **Booking Creation**: 
   - User creates booking via API
   - `BookingViewSet.perform_create()` triggers `send_booking_confirmation_email.delay()`
   - Email sent asynchronously

2. **Payment Confirmation**:
   - Payment verification triggers `send_payment_confirmation_email.delay()`
   - Email sent asynchronously

## Troubleshooting

### Common Issues:
1. **Connection refused**: Ensure RabbitMQ is running
2. **Email not sending**: Check email configuration in `.env`
3. **Tasks not executing**: Verify Celery worker is running
4. **Import errors**: Ensure all dependencies are installed

### Debug Commands:
```bash
# Check Celery status
celery -A alx_travel_app status

# Inspect active tasks
celery -A alx_travel_app inspect active

# Purge all tasks
celery -A alx_travel_app purge
```
