from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    address = models.CharField("Address", max_length=200, blank=True)
    use_yn = models.CharField("Active Status", max_length=1, choices=[('Y', 'Used'), ('N', 'Unused')], default='Y')


    def __str__(self):
        return f"{self.user.username} - {self.user}"


class CustomerInfo(models.Model):
    name = models.CharField()
    address = models.CharField()
    customerTpin = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_created")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="user_updated", null=True, blank=True)


    def __str__(self):
        return self.name