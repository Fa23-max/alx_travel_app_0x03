from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ListingViewSet, BookingViewSet

router = DefaultRouter()
router.register(r'listings', ListingViewSet)
router.register(r'bookings', BookingViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
    path('api/payments/initiate/', views.initiate_payment, name='initiate-payment'),
    path('api/payments/verify/', views.verify_payment, name='verify-payment'),
]
