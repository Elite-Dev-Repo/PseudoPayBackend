from django.dispatch import receiver
from django.db.models.signals import post_save
from .models import User, MerchantProfile, EmailVerificationToken
from .emails import send_html_email
from django.conf import settings
from Wallet.models import Transaction

@receiver(post_save, sender=User)
def create_email_verification_token(sender, instance, created, **kwargs):
    if created:
        if instance.is_active != True:
            EmailVerificationToken.objects.create(user=instance)


@receiver(post_save, sender=User)
def create_merchant_profile(sender, instance, created, **kwargs):
    if created:
        MerchantProfile.objects.create(user=instance)


@receiver(post_save, sender=EmailVerificationToken)
def send_email_verification_token(sender, instance, created, **kwargs):
    if created:
        user = instance.user
        name = user.first_name + " " + user.last_name
        send_html_email(
            subject='Verify Your Email Address - PseudoPay',
            template_name='emails/email_verification.html',
            context={
                'user': name,
                'token': instance.token,
            },
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[instance.user.email],
        )
