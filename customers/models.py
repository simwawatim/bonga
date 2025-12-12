import uuid
import os
from django_tenants.models import TenantMixin, DomainMixin
from django.db import models

def client_logo_upload_to(instance, filename):
    """
    Generate a unique filename using UUID for each uploaded logo.
    """
    ext = filename.split('.')[-1]  # get file extension
    filename = f"{uuid.uuid4()}.{ext}"  # new filename with UUID
    return os.path.join('client_logos', filename)

class Client(TenantMixin):
    name = models.CharField(max_length=100)
    paid_until = models.DateField()
    on_trial = models.BooleanField(default=True)
    zra_tpin = models.CharField(max_length=20, unique=True, verbose_name="ZRA TPIN")
    business_name = models.CharField(max_length=150, blank=True, null=True)
    business_address = models.TextField(blank=True, null=True)
    contact_email = models.EmailField(blank=True, null=True)
    contact_phone = models.CharField(max_length=20, blank=True, null=True)
    
    logo = models.ImageField(
        upload_to=client_logo_upload_to,  # use the custom function
        blank=True, 
        null=True, 
        default='client_logos/default.png'
    )
    primary_color = models.CharField(
        max_length=7, 
        blank=True, 
        null=True, 
        default='#000000', 
        help_text="HEX color code, e.g. #000000"
    )
    secondary_color = models.CharField(
        max_length=7, 
        blank=True, 
        null=True, 
        default='#000000', 
        help_text="HEX color code, e.g. #000000"
    )

    auto_create_schema = True

    def __str__(self):
        return f"{self.name} ({self.zra_tpin})"


class Domain(DomainMixin):
    pass
