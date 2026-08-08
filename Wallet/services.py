from core.emails import send_html_email
from django.conf import settings

def send_transaction_email(user, transaction):
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