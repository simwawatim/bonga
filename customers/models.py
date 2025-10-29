from django_tenants.models import TenantMixin, DomainMixin
from django.db import models

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=True)
    zra_tpin = models.CharField(max_length=20, unique=True, verbose_name="ZRA TPIN")
    business_name = models.CharField(max_length=150, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    auto_create_schema = True

    def __str__(self):
        return f"{self.name} ({self.zra_tpin})"


class Domain(DomainMixin):
    pass
