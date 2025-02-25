from django.core.mail import EmailMultiAlternatives


def send_email(subject, recipient_list, text_content, html_content):
    """
    A reusable function to send emails.

    :param subject: Subject of the email
    :param recipient_list: List of email recipients
    :param text_content: Plain text version of the email
    :param html_content: HTML version of the email
    """
    from_email = "no-reply@example.com"

    email = EmailMultiAlternatives(subject, text_content, from_email, recipient_list)
    email.attach_alternative(html_content, "text/html")
    email.send()
