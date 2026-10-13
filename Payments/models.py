from django.db import models
from core.models import User, MerchantProfile

# Create your models here.


class IdempotencyRecord(models.Model):
    RECORD_STATUS = [
        ('Processing', "Processing"),
        ("Completed", "Completed")
    ]
    key = models.UUIDField()
    profile = models.ForeignKey(MerchantProfile, on_delete=models.CASCADE, related_name="user_idempotency_record")
    request_hash = models.CharField(max_length=70)
    status = models.CharField(max_length=15, choices=RECORD_STATUS )
    response_status = models.PositiveBigIntegerField(  null=True, blank=True)
    response_body = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["profile", "key"],
                name="user_idempotency_key_constraint"
                
            )
        ]