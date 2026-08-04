from django.db import models
import hashlib
import secrets
from django.contrib.auth import get_user_model


User = get_user_model()
# Create your models here.


class ApiKey(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='api_keys')
    key = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=100)
    prefix = models.CharField(max_length=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)


    @classmethod
    def generate_key(cls, user, name): 
        raw_key = f"sk_pseudo_{secrets.token_urlsafe(32)}"
        prefix = raw_key[:10]
        hashed_key = hashlib.sha256(raw_key.encode()).hexdigest()
        key_obj = cls.objects.create(
            user=user,
            name=name,
            prefix=prefix,
            key=hashed_key
            )

        return key_obj, raw_key

    def __str__(self):
        return f"Api key - {self.prefix} for {self.user.email}"
