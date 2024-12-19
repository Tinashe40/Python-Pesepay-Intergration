import string

class Response:

    def __init__(self, success, message = None, referenceNumber = None, pollUrl = None, redirectUrl = None, paid = False):
        self.success = success
        self.message = message
        self.referenceNumber = referenceNumber
        self.pollUrl = pollUrl
        self.redirectUrl = redirectUrl
        self.paid = paid

        