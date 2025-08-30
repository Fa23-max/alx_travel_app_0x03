from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings
from .models import Payment, Booking

@shared_task
def send_payment_confirmation_email(payment_id):
    """
    Send payment confirmation email to the user.
    """
    try:
        payment = Payment.objects.get(payment_id=payment_id)
        booking = payment.booking
        user = booking.user
        
        subject = f"Payment Confirmation for Booking {booking.booking_id.hex[:8]}"
        message = f"""
        Hello {user.first_name or user.username},
        
        Your payment for booking {booking.listing.name} has been confirmed.
        
        Booking Details:
        - Listing: {booking.listing.name}
        - Dates: {booking.start_date} to {booking.end_date}
        - Total Amount: {payment.amount} ETB
        - Payment ID: {payment.payment_id}
        
        Thank you for using our service!
        
        Best regards,
        ALX Travel Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL if hasattr(settings, 'DEFAULT_FROM_EMAIL') else 'no-reply@alxtravel.com',
            [user.email],
            fail_silently=False,
        )
        
        return f"Confirmation email sent to {user.email}"
    except Payment.DoesNotExist:
        return f"Payment with ID {payment_id} does not exist"
    except Exception as e:
        return f"Failed to send email: {str(e)}"


@shared_task
def send_booking_confirmation_email(booking_id):
    """
    Send booking confirmation email to the user when a booking is created.
    """
    try:
        booking = Booking.objects.get(booking_id=booking_id)
        user = booking.user
        listing = booking.listing
        
        subject = f"Booking Confirmation - {listing.name}"
        message = f"""
        Hello {user.first_name or user.username or 'Valued Customer'},
        
        Your booking has been successfully created!
        
        Booking Details:
        - Booking ID: {booking.booking_id}
        - Listing: {listing.name}
        - Location: {listing.location}
        - Check-in: {booking.start_date}
        - Check-out: {booking.end_date}
        - Total Price: ${booking.total_price}
        - Status: {booking.get_status_display()}
        
        Host Information:
        - Host: {listing.host.first_name or listing.host.username or 'Host'}
        - Contact: {listing.host.email}
        
        We'll send you another confirmation once your payment is processed.
        
        Thank you for choosing ALX Travel!
        
        Best regards,
        ALX Travel Team
        """
        
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        
        return f"Booking confirmation email sent to {user.email}"
    except Booking.DoesNotExist:
        return f"Booking with ID {booking_id} does not exist"
    except Exception as e:
        return f"Failed to send booking confirmation email: {str(e)}"