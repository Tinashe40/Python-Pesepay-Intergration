from django.urls import path
from . import views

urlpatterns = [
    path("initiate/", views.initiate_payment, name="initiate"),
    path("return/", views.PaymentReturnView.as_view(), name="payment_return"),
]
