from django.test import TestCase
from django.core import mail
from django.contrib.auth import get_user_model
from core.models import EmailVerificationToken
from core.emails import send_html_email

class EmailServiceTests(TestCase):
    def setUp(self):
        # We need to construct a user. Note that date_of_birth is required in class User model definition
        self.user = get_user_model().objects.create_user(
            email='testuser@example.com',
            password='testpassword123',
            first_name='Test',
            last_name='User',
            date_of_birth='2000-01-01',
            gender='Male'
        )

    def test_send_html_email_directly(self):
        # Send email manually via the service
        subject = 'Direct Test Subject'
        template_name = 'emails/email_verification.html'
        context = {
            'user': self.user,
            'token': 'TESTTOKEN1234'
        }
        recipient_list = ['recipient@example.com']

        send_html_email(subject, template_name, context, recipient_list)

        # Check outbox
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, subject)
        self.assertEqual(email.to, recipient_list)
        
        # Verify both plain text and HTML alternatives exist
        self.assertIn('TESTTOKEN1234', email.body)
        self.assertEqual(len(email.alternatives), 1)
        html_part, content_type = email.alternatives[0]
        self.assertEqual(content_type, 'text/html')
        self.assertIn('TESTTOKEN1234', html_part)
        self.assertIn('Verify Your Email - PseudoPay', html_part)

    def test_signal_sends_email_on_user_creation_with_verification(self):
        # Let's clear any setup emails
        mail.outbox.clear()
        
        # Create a new user to test the signal sequence
        new_user = get_user_model().objects.create_user(
            email='signaluser@example.com',
            password='testpassword123',
            first_name='Signal',
            last_name='User',
            date_of_birth='1995-05-15',
            gender='Female'
        )
        
        # When user with is_active=False is created, a token must be created, triggering send_email_verification_token post_save signal
        token_exists = EmailVerificationToken.objects.filter(user=new_user).exists()
        self.assertTrue(token_exists)
        
        # Should have sent 1 email
        self.assertEqual(len(mail.outbox), 1)
        email = mail.outbox[0]
        self.assertEqual(email.subject, 'Verify Your Email Address - PseudoPay')
        self.assertEqual(email.to, ['signaluser@example.com'])
        
        token = EmailVerificationToken.objects.get(user=new_user).token
        self.assertIn(token, email.body)
        
        # Verify HTML alternative
        html_part, content_type = email.alternatives[0]
        self.assertEqual(content_type, 'text/html')
        self.assertIn(token, html_part)

