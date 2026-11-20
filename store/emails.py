from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import smtplib


def send_templated_email(subject, template_name, context, recipient):
    text_body = render_to_string(f"emails/{template_name}.txt", context)
    html_body = render_to_string(f"emails/{template_name}.html", context)
    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.attach_alternative(html_body, "text/html")
    sent_count = email.send()
    if sent_count != 1:
        raise smtplib.SMTPException(
            f"Expected to send one email, but sent {sent_count}."
        )
    return sent_count
