from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_html_email(subject, template_name, context, recipient_list, from_email=None):
    """
    Sends a reusable HTML email with full HTML formatting and a fallback text description.
    
    :param subject: Email subject.
    :param template_name: Path to the HTML template relative to directory in TEMPLATES (e.g. 'emails/email_verification.html').
    :param context: Context dictionary to render template variables.
    :param recipient_list: List of recipient email addresses.
    :param from_email: Sender email address (defaults to DEFAULT_FROM_EMAIL or EMAIL_HOST_USER).
    """
    if not from_email:
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', getattr(settings, 'EMAIL_HOST_USER', 'no-reply@pseudopay.com'))

    # Render HTML representation
    html_content = render_to_string(template_name, context)

    # Render Plain Text representation
    # Check if a .txt template exists with the same base name, otherwise strip tags from HTML
    text_template_name = template_name.replace('.html', '.txt')
    try:
        text_content = render_to_string(text_template_name, context)
    except Exception:
        text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_content,
        from_email=from_email,
        to=recipient_list
    )
    email.attach_alternative(html_content, "text/html")
    return email.send(fail_silently=False)
