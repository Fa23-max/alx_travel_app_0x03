#!/usr/bin/env python
"""
Test script for Celery background tasks.
Run this script to test if Celery is properly configured and tasks are working.
"""

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'alx_travel_app.settings')
django.setup()

from alx_travel_app.listings.tasks import send_booking_confirmation_email, send_payment_confirmation_email
from alx_travel_app.listings.models import Booking, Payment
from django.contrib.auth.models import User

def test_celery_tasks():
    """Test Celery tasks functionality."""
    print("Testing Celery Tasks...")
    
    # Test 1: Check if we can import tasks
    try:
        print("✓ Tasks imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import tasks: {e}")
        return
    
    # Test 2: Check if we have any bookings to test with
    bookings = Booking.objects.all()
    if bookings.exists():
        booking = bookings.first()
        print(f"✓ Found booking: {booking.booking_id}")
        
        # Test booking confirmation email
        try:
            result = send_booking_confirmation_email.delay(str(booking.booking_id))
            print(f"✓ Booking confirmation email task queued: {result.id}")
        except Exception as e:
            print(f"✗ Failed to queue booking confirmation email: {e}")
    else:
        print("! No bookings found. Create a booking first to test email functionality.")
    
    # Test 3: Check if we have any payments to test with
    payments = Payment.objects.all()
    if payments.exists():
        payment = payments.first()
        print(f"✓ Found payment: {payment.payment_id}")
        
        # Test payment confirmation email
        try:
            result = send_payment_confirmation_email.delay(str(payment.payment_id))
            print(f"✓ Payment confirmation email task queued: {result.id}")
        except Exception as e:
            print(f"✗ Failed to queue payment confirmation email: {e}")
    else:
        print("! No payments found. Create a payment first to test payment email functionality.")
    
    print("\nCelery configuration check:")
    print(f"Broker URL: {settings.CELERY_BROKER_URL}")
    print(f"Result Backend: {settings.CELERY_RESULT_BACKEND}")
    print(f"Email Backend: {settings.EMAIL_BACKEND}")
    print(f"Default From Email: {settings.DEFAULT_FROM_EMAIL}")

if __name__ == "__main__":
    test_celery_tasks()
