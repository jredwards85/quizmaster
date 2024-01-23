from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

def is_user_online(user):
    if user.is_authenticated:
        now = timezone.now()
        last_activity = user.last_activity
        return now <= last_activity + timezone.timedelta(minutes=5)
    return False