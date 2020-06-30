import json
import requests
from django.conf import settings
from rest_framework.reverse import reverse

from ..models import Payment, CreditCardInfo


def initiate_payment(request, payment_data: Payment, card: CreditCardInfo):
    url = settings.MYFATOORAH.PAYMENT_URL + "/v2/ExecutePayment"
    request_data = {
        'PaymentMethodId': 2,
        'CustomerName': request.user.name,
        'CustomerEmail': request.user.email,
        'InvoiceValue': str(payment_data.amount),
        'DisplayCurrencyIso': payment_data.currency,
        'CallBackUrl': reverse('payments-success', request=request, kwargs={'pk': payment_data.pk}),
        'ErrorUrl': reverse('payments-error', request=request, kwargs={'pk': payment_data.pk}),
        'Language': 'en',
        'UserDefinedField': 'Payment_' + str(payment_data.id)
    }
    headers = {'Content-Type': "application/json", 'Authorization': "Bearer " + settings.MYFATOORAH.API_KEY}
    response = requests.request("POST", url, data=json.dumps(request_data), headers=headers)
    json_response = response.json()

    if response.status_code > 210:
        return response
    data = json_response['Data']
    payment_url = data['PaymentURL']

    print("PaymentURL  Response:\n" + payment_url)

    # after getting the payment url call it as a post API and pass card info to it
    # if you saved the card info before you can pass the token for the api
    payload = {
        'paymentType': 'card',
        'card': {
            'Number': card.card,
            'expiryMonth': card.exp_month,
            'expiryYear': card.exp_year,
            'securityCode': card.cvc
        },
        'saveToken': False
    }
    # payload = "{\"paymentType\": \"card\",\"card\": {\"Number\":\"5123450000000008\",\"expiryMonth\":\"05\"," \
    #           "\"expiryYear\":\"21\",\"securityCode\":\"100\"},\"saveToken\": false} "
    headers = {'Content-Type': "application/json", 'Authorization': "Bearer " + settings.MYFATOORAH.API_KEY}
    return requests.request("POST", payment_url, data=json.dumps(payload), headers=headers)
