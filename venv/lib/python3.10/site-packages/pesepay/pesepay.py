import base64
import string
import jsonpickle
import requests
from Crypto.Cipher import AES

from pesepay.payments import (TransactionDetailsHolder,
                              Transaction, Customer, Payment, Amount)

from pesepay.response import Response

BS = AES.block_size
pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)
unpad = lambda s: s[0:-ord(s[-1:])]

BASE_URL = 'https://api.pesepay.com/api/payments-engine'
CHECK_PAYMENT_URL = BASE_URL + '/v1/payments/check-payment'
MAKE_SEAMLESS_PAYMENT_URL = BASE_URL + '/v2/payments/make-payment'
MAKE_PAYMENT_URL = BASE_URL + '/v1/payments/make-payment/secure'
INITIATE_PAYMENT_URL = BASE_URL + '/v1/payments/initiate'


class Pesepay:
    result_url: string = None
    return_url: string = None

    def __init__(self, integration_key: string, encryption_key: string):
        self.integration_key = integration_key
        self.encryption_key = encryption_key
        self.headers = {'key': integration_key, 'Content-Type': 'application/json'}

    def initiate_transaction(self, transaction: Transaction) -> Response:
        if self.result_url is None:
            raise InvalidRequestException('Result url has not been specified')

        if self.return_url is None:
            raise InvalidRequestException('Return url has not been specified')

        transaction.resultUrl = self.result_url
        transaction.returnUrl = self.return_url

        raw_request = jsonpickle.encode(transaction.__dict__)

        encrypted_request = TransactionDetailsHolder(self.__encrypt(raw_request))

        server_response = requests.post(INITIATE_PAYMENT_URL, data=jsonpickle.encode(encrypted_request),
                                        headers=self.headers)
        server_response_json = server_response.json()

        if server_response.status_code == 200:
            raw_response = self.__decrypt(server_response_json.get('payload'))
            json_string = jsonpickle.decode(raw_response)
            ref_no = json_string.get('referenceNumber')
            poll_url = json_string.get('pollUrl')
            redirect_url = json_string.get('redirectUrl')
            return Response(True, referenceNumber=ref_no, pollUrl=poll_url, redirectUrl=redirect_url)
        else:
            message = server_response_json.get('message')
            return Response(False, message)

    def make_seamless_payment(self, payment: Payment, reason_for_payment: string, amount: float,
                              required_fields: dict = None) -> Response:
        if self.result_url is None:
            raise InvalidRequestException('Result url has not been specified')

        payment.resultUrl = self.result_url
        payment.returnUrl = self.return_url
        payment.reasonForPayment = reason_for_payment
        payment.amountDetails = Amount(amount, payment.currencyCode)
        payment.paymentMethodRequiredFields = required_fields

        raw_request = jsonpickle.encode(payment.__dict__)

        encrypted_request = TransactionDetailsHolder(self.__encrypt(raw_request))

        server_response = requests.post(MAKE_SEAMLESS_PAYMENT_URL, data=jsonpickle.encode(encrypted_request),
                                        headers=self.headers)
        server_response_json = server_response.json()

        if server_response.status_code == 200:
            raw_response = self.__decrypt(server_response_json.get('payload'))
            json_string = jsonpickle.decode(raw_response)
            ref_no = json_string.get("referenceNumber")
            status = json_string.get("transactionStatus")
            poll_url = json_string.get("pollUrl")
            redirect_url = json_string.get("redirectUrl")
            return Response(True, None, ref_no, poll_url, redirect_url, status == 'SUCCESS')
        else:
            message = server_response_json.get('message')
            return Response(False, message)

    def check_payment(self, reference_number: string) -> Response:
        url = CHECK_PAYMENT_URL + '?referenceNumber=' + reference_number
        return self.poll_transaction(url)

    def poll_transaction(self, poll_url) -> Response:
        server_response = requests.get(poll_url, headers=self.headers)
        server_response_json = server_response.json()

        if server_response.status_code == 200:
            raw_response = self.__decrypt(server_response_json.get('payload'))
            json_string = jsonpickle.decode(raw_response)
            ref_no = json_string.get("referenceNumber")
            status = json_string.get("transactionStatus")
            poll_url = json_string.get("pollUrl")
            redirect_url = json_string.get("redirectUrl")
            return Response(True, None, ref_no, poll_url, redirect_url, status == 'SUCCESS')
        else:
            message = server_response_json.get('message')
            return Response(False, message)

    def create_payment(self, currency_code: string, payment_method_code: string, email: string = None,
                       phone: string = None, name: string = None):
        if email == None and phone == None:
            raise InvalidRequestException('Email and/or phone number should be provided')

        customer = Customer(email, phone, name)
        return Payment(currency_code, payment_method_code, customer)

    def create_transaction(self, amount: float, currency_code: string,
                           payment_reason: string, merchant_reference: string = None):
        return Transaction(amount, currency_code, payment_reason, merchant_reference)

    def __encrypt(self, payload):
        init_vector = self.encryption_key[0:16]
        cryptor = AES.new(self.encryption_key.encode("utf8"), AES.MODE_CBC, init_vector.encode("utf8"))
        ciphertext = cryptor.encrypt(bytes(pad(payload), encoding="utf8"))
        return base64.b64encode(ciphertext).decode('utf-8')

    def __decrypt(self, payload):
        decode = base64.b64decode(payload)
        init_vector = self.encryption_key[0:16]
        cryptor = AES.new(self.encryption_key.encode("utf8"), AES.MODE_CBC, init_vector.encode("utf8"))
        plain_text = cryptor.decrypt(decode)
        return unpad(plain_text).decode('utf-8')

class InvalidRequestException(Exception):
    def __init__(self, message):
        super(InvalidRequestException, self).__init__(message)