import string

import jsonpickle


class Customer:
    def __init__(self, email: string = None, phone_number: string = None, name: string = None):
        self.email = email
        self.phoneNumber = phone_number
        self.name = name


class Amount:
    def __init__(self, amount: float, currency_code: string):
        self.amount = amount
        self.currencyCode = currency_code

    @staticmethod
    def from_json(json_string):
        return Amount(json_string.get("amount"), json_string.get("currencyCode"))


class Transaction:
    resultUrl: string
    returnUrl: string

    def __init__(self, amount: float, currency_code: string,
                 reason_for_payment: string, merchant_reference: string = None):
        self.amountDetails = Amount(amount, currency_code)
        self.transactionType = "BASIC"
        self.reasonForPayment = reason_for_payment
        self.merchantReference = merchant_reference


class Payment:
    referenceNumber: string
    amountDetails: Amount
    reasonForPayment: string
    paymentRequestFields: dict
    paymentMethodRequiredFields: dict
    merchantReference: string
    returnUrl: string
    resultUrl: string

    def __init__(self, currencyCode: string, paymentMethodCode: string, customer: Customer):
        self.currencyCode = currencyCode
        self.paymentMethodCode = paymentMethodCode
        self.customer = customer


class TransactionDetailsHolder:
    def __init__(self, payload: string):
        self.payload = payload
