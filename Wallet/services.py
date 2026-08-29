from Wallet.webhooks import WebhookHandler
from core.emails import send_html_email
from django.conf import settings

def send_transaction_email(transaction):
    user = transaction.customer_name
    send_html_email(
        subject='Transaction Alert - PseudoPay',
        template_name='emails/transaction.html',
        context={
            'user': user,
            'transaction': transaction,
        },
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[transaction.customer_email],
    )


def on_transaction_commit(transaction):
    send_transaction_email(transaction)
    WebhookHandler(transaction).send_webhook()


def send_reset_link_email(link, user_email):
    send_html_email(
        subject='Password Reset Request - PseudoPay',
        template_name='emails/reset_password_email.html',
        context={
            "reset_link": link,
            "data": link,  # keep for backwards compat with old template
            "user_email": user_email,
        },
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
    )
