import requests
from django.conf import settings
import json



class WebhookHandler:
    def __init__(self, transaction):
        self.transaction = transaction

    def send_webhook(self):
        url = self.transaction.wallet.profile.request_origin
        # url = "https://warm-phoenix-48.webhook.cool"
        if not url:
            return
        payload = {
            'transaction_id': self.transaction.id,
            'amount': str(self.transaction.amount),
            'status': self.transaction.transaction_status,
            'created_at': self.transaction.created_at.isoformat(),
        }
        try:
            requests.post(url, data=json.dumps(payload), headers={'Content-Type': 'application/json'})
        except Exception as e:
            print(f"Webhook failed: {e}")