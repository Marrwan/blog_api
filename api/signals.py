from datetime import timezone, datetime

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Comment, Post

@receiver(post_save, sender=Comment)
def update_post_last_updated(sender, instance, **kwargs):
    post = instance.post
    post.last_updated = datetime.now()
    post.save()
