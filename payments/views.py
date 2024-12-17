import logging
import uuid

from django.conf import settings
from django.shortcuts import redirect, render
from django.views import View
from pesepay import Pesepay
from django.http import HttpResponseNotAllowed

from .models import Donation, Payment

logger = logging.getLogger(__name__)

# Initialize Pesepay instance with integration and encryption keys
pesepay = Pesepay(settings.PESEPAY_INTEGRATION_KEY, settings.PESEPAY_ENCRYPTION_KEY)

# Initiate Payment
def initiate_payment(request):
    if request.method == "POST":
        amount = request.POST.get("amount")
        currency = request.POST.get("currency")
        payment_reason = request.POST.get("payment_reason", "Donation")

        try:
            # Generate a unique placeholder for the reference number
            unique_placeholder = str(uuid.uuid4())
            payment = Payment.objects.create(reference_number=unique_placeholder)

            pesepay.return_url = f'http://127.0.0.1:8000/payment/return?payment_id={payment.payment_id}'
            pesepay.result_url = 'http://127.0.0.1:8000/payment/result/'

            # Create a transaction
            transaction = pesepay.create_transaction(amount, currency, payment_reason)

            # Initiate the transaction
            response = pesepay.initiate_transaction(transaction)

            logger.debug(f"Pesepay response: {response}")

            if response.success:
                # Ensure the correct attribute names are used
                reference_number = getattr(response, 'referenceNumber', None)
                redirect_url = getattr(response, 'redirectUrl', None)

                if not reference_number or not redirect_url:
                    return render(request, "error.html", {
                        "message": "Response is missing necessary attributes."
                    })

                # Update the Payment instance with the actual reference number
                payment.reference_number = reference_number
                payment.save()

                # Create the Donation object
                Donation.objects.create(
                    payment=payment,
                    amount=amount,
                    currency_code=currency,
                    payment_reason=payment_reason,
                    status='Pending',
                )

                # Redirect user to Pesepay to complete the payment
                return redirect(redirect_url)
            else:
                # Handle error response
                return render(request, "payment_failure.html", {"message": response.message})
        except Exception as e:
            logger.error(f"Error initiating payment: {str(e)}")
            return render(request, "error.html", {"message": "An error occurred while initiating the payment."})

    return render(request, "initiate_payment.html")


# Handle Payment Return
class PaymentReturnView(View):
    def get(self, request):
        # Retrieve the payment_id from the query parameters
        payment_id = request.GET.get("payment_id")

        if not payment_id:
            logger.error("Payment ID not provided in return URL.")
            return render(request, 'error.html', {'message': 'Payment ID not provided.'})

        try:
            # Fetch the payment and donation details from the database
            payment = Payment.objects.get(payment_id=payment_id)
            donation = Donation.objects.get(payment=payment)

            # Get the Pesepay response for the status
            response = pesepay.check_payment(payment.reference_number)

            logger.debug(f"Pesepay payment status response: {response}")

            # Extract fields for the response and database
            amount = donation.amount
            currency_code = donation.currency_code
            payment_reason = donation.payment_reason

            # Extract fields from Pesepay response
            status = 'Paid' if getattr(response, 'paid', False) else 'Incomplete'

            # Prepare context without 'status', 'reference_number', or 'fees' from the database
            context = {
                'status': status,  # Derived from Pesepay response
                'reason_for_payment': payment_reason,
                'amount': amount,
                'currency': currency_code,
                 'reference': payment.reference_number, 
            }

            # If the transaction is successful, update the donation status
            if status == 'Paid':
                donation.status = 'Paid'
                donation.save()

            return render(request, 'payment_return.html', context)

        except Payment.DoesNotExist:
            logger.error(f"Payment with ID {payment_id} not found.")
            return render(request, 'error.html', {'message': 'Payment not found.'})
        except Donation.DoesNotExist:
            logger.error(f"Donation linked to payment ID {payment_id} not found.")
            return render(request, 'error.html', {'message': 'Donation not found.'})
        except Exception as e:
            logger.error(f"Unhandled error in PaymentReturnView: {str(e)}")
            return render(request, 'error.html', {'message': f"An error occurred: {str(e)}"})
