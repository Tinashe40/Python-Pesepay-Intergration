from django.urls import path
from . import views
from .views import initiate_payment

urlpatterns = [
  path('', initiate_payment, name='initiate'),
  path("initiate/", views.initiate_payment, name="initiate"),
  path("return/", views.PaymentReturnView.as_view(), name="payment_return"),
]
