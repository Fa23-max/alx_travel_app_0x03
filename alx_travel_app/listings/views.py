from django.shortcuts import render

# Create your views here.
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from .models import Listing, Booking
from .serializers import ListingSerializer, BookingSerializer
from .tasks import send_booking_confirmation_email

class ListingViewSet(viewsets.ModelViewSet):
    queryset = Listing.objects.all()
    serializer_class = ListingSerializer

class BookingViewSet(viewsets.ModelViewSet):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    
    def perform_create(self, serializer):
        """
        Override perform_create to trigger email task after booking creation.
        """
        booking = serializer.save()
        # Trigger booking confirmation email task asynchronously
        send_booking_confirmation_email.delay(str(booking.booking_id))
        return booking


# --- Payment Views ---
import requests
import uuid
from django.conf import settings
from django.http import JsonResponse
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Booking, Payment
from .serializers import PaymentSerializer, PaymentInitiationSerializer

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_payment(request):
    """
    Initiate a payment for a booking by making a POST request to Chapa API.
    """
    serializer = PaymentInitiationSerializer(data=request.data)
    if serializer.is_valid():
        booking_id = serializer.validated_data['booking_id']
        
        try:
            booking = Booking.objects.get(booking_id=booking_id)
        except Booking.DoesNotExist:
            return Response(
                {'error': 'Booking not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create a payment record with pending status
        payment = Payment.objects.create(
            booking=booking,
            amount=booking.total_price,
            status='pending'
        )
        
        # Prepare data for Chapa API
        chapa_data = {
            'amount': str(booking.total_price),
            'currency': 'ETB',  # Ethiopian Birr
            'email': request.user.email,
            'first_name': getattr(request.user, 'first_name', ''),
            'last_name': getattr(request.user, 'last_name', ''),
            'tx_ref': str(payment.payment_id),  # Use payment_id as transaction reference
            'callback_url': request.build_absolute_uri('/api/payments/verify/'),
            'return_url': request.build_absolute_uri('/payment/success/'),
            'customization': {
                'title': f'Payment for {booking.listing.name}',
                'description': f'Booking from {booking.start_date} to {booking.end_date}'
            }
        }
        
        # Make request to Chapa API
        try:
            response = requests.post(
                'https://api.chapa.co/v1/transaction/initialize',
                json=chapa_data,
                headers={
                    'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}'
                }
            )
            response_data = response.json()
            
            if response_data.get('status') == 'success':
                # Update payment with transaction ID
                payment.transaction_id = response_data.get('data', {}).get('checkout_url')
                payment.save()
                
                return Response({
                    'payment_id': payment.payment_id,
                    'checkout_url': response_data.get('data', {}).get('checkout_url')
                }, status=status.HTTP_200_OK)
            else:
                # Update payment status to failed
                payment.status = 'failed'
                payment.save()
                return Response({
                    'error': response_data.get('message', 'Payment initiation failed')
                }, status=status.HTTP_400_BAD_REQUEST)
                
        except requests.RequestException as e:
            # Update payment status to failed
            payment.status = 'failed'
            payment.save()
            return Response({
                'error': 'Payment service unavailable'
            }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    """
    Verify payment status with Chapa after user completes payment.
    """
    tx_ref = request.GET.get('tx_ref')
    
    if not tx_ref:
        return Response({
            'error': 'Transaction reference is required'
        }, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        payment = Payment.objects.get(payment_id=tx_ref)
    except Payment.DoesNotExist:
        return Response({
            'error': 'Payment not found'
        }, status=status.HTTP_404_NOT_FOUND)
    
    # Make request to Chapa API to verify payment
    try:
        response = requests.get(
            f'https://api.chapa.co/v1/transaction/verify/{tx_ref}',
            headers={
                'Authorization': f'Bearer {settings.CHAPA_SECRET_KEY}'
            }
        )
        response_data = response.json()
        
        if response_data.get('status') == 'success' or response_data.get('data', {}).get('status') == 'success':
            # Update payment status to completed
            payment.status = 'completed'
            payment.save()
            
            # Update booking status to confirmed
            payment.booking.status = 'confirmed'
            payment.booking.save()
            
            # Send confirmation email using Celery
            from .tasks import send_payment_confirmation_email
            send_payment_confirmation_email.delay(payment.payment_id)
            
            return Response({
                'message': 'Payment verified successfully',
                'payment_status': 'completed'
            }, status=status.HTTP_200_OK)
        else:
            # Update payment status to failed
            payment.status = 'failed'
            payment.save()
            return Response({
                'message': 'Payment verification failed',
                'payment_status': 'failed'
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except requests.RequestException as e:
        return Response({
            'error': 'Payment verification service unavailable'
        }, status=status.HTTP_503_SERVICE_UNAVAILABLE)
