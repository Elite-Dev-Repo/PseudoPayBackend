import requests
from django.conf import settings



class WebhookHandler:
    def __init__(self, transaction):
        self.transaction = transaction

    def send_webhook(self):
        url = self.transaction.wallet.profile.request_origin
        if not url:
            return
        payload = {
            'transaction_id': self.transaction.id,
            'amount': self.transaction.amount,
            'status': self.transaction.status,
            'created_at': self.transaction.created_at.isoformat(),
        }
        try:
            requests.post(url, json=payload, timeout=5, headers={'Content-Type': 'application/json'})
        except Exception as e:
            print(f"Webhook failed: {e}")