"""
Test script for Chapa payment integration.
This script demonstrates how to use the payment API endpoints.
"""

import requests
import json

# Base URL for the API
BASE_URL = 'http://127.0.0.1:8000/api'

def test_payment_workflow():
    """
    Test the complete payment workflow.
    Note: This requires the Django server to be running.
    """
    print("Testing Chapa Payment Integration")
    print("=" * 40)
    
    # Step 1: Initiate payment
    print("\n1. Initiating payment...")
    payment_data = {
        "booking_id": "test-booking-id"  # In a real scenario, this would be a valid booking ID
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/payments/initiate/",
            json=payment_data,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code == 200:
            print("   Payment initiated successfully!")
            print(f"   Response: {response.json()}")
        else:
            print(f"   Failed to initiate payment: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Error initiating payment: {e}")
    
    # Step 2: Verify payment
    print("\n2. Verifying payment...")
    try:
        # In a real scenario, this would be called by Chapa's webhook
        # or when the user returns from the payment page
        response = requests.get(
            f"{BASE_URL}/payments/verify/",
            params={"tx_ref": "test-payment-id"}
        )
        
        if response.status_code == 200:
            print("   Payment verified successfully!")
            print(f"   Response: {response.json()}")
        else:
            print(f"   Failed to verify payment: {response.status_code}")
            print(f"   Response: {response.text}")
    except requests.exceptions.RequestException as e:
        print(f"   Error verifying payment: {e}")

if __name__ == "__main__":
    test_payment_workflow()
    print("\n" + "=" * 40)
    print("Test completed. Check the output above.")