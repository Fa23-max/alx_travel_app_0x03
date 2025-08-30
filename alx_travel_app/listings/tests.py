from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Listing, Booking, Payment
import uuid

User = get_user_model()

class PaymentModelTest(TestCase):
    def setUp(self):
        # Create a user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create a listing
        self.listing = Listing.objects.create(
            host=self.user,
            name='Test Listing',
            description='Test description',
            location='Test Location',
            pricepernight=100.00
        )
        
        # Create a booking
        self.booking = Booking.objects.create(
            listing=self.listing,
            user=self.user,
            start_date='2023-01-01',
            end_date='2023-01-05',
            total_price=400.00
        )
    
    def test_payment_creation(self):
        """Test that a payment can be created"""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=400.00,
            status='pending'
        )
        
        self.assertEqual(payment.booking, self.booking)
        self.assertEqual(payment.amount, 400.00)
        self.assertEqual(payment.status, 'pending')
        self.assertIsNotNone(payment.payment_id)
    
    def test_payment_string_representation(self):
        """Test the string representation of a payment"""
        payment = Payment.objects.create(
            booking=self.booking,
            amount=400.00,
            status='completed'
        )
        
        expected_str = f"Payment {payment.payment_id.hex[:8]} for Booking {self.booking.booking_id.hex[:8]} - completed"
        self.assertEqual(str(payment), expected_str)
