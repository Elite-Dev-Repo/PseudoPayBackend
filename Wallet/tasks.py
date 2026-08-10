from celery import shared_task
from .services import on_transaction_commit

@shared_task
def on_transaction_commit_task(transaction):
    on_transaction_commit(transaction)
