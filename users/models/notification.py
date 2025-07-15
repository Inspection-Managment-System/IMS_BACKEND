from django.db import models

from .user import User
from ims_backend.utils.send_email import send_email


class Notification(models.Model):
    sender = models.ForeignKey(
        User, related_name="sent_messages", on_delete=models.CASCADE
    )
    recipient = models.ForeignKey(
        User, related_name="received_messages", on_delete=models.CASCADE
    )
    content = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"From {self.sender.username} to {self.recipient.username} at {self.timestamp}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and self.recipient and self.recipient.email:
            try:
                send_email(
                    subject="New Notification from Inspection Management System",
                    recipient_list=[self.recipient.email],
                    text_content=self.content,
                    html_content=f"<p>{self.content}</p>",
                )
            except Exception as e:
                # Optionally log the error
                pass
