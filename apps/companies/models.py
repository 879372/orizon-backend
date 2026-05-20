from django.db import models
from uuid import uuid4

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    logo = models.ImageField(upload_to='logos/', null=True, blank=True)
    plan = models.CharField(max_length=20, choices=[
        ('basic', 'Basic'),
        ('pro', 'Pro'),
        ('enterprise', 'Enterprise'),
    ], default='basic')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
    
class CompanySettings(models.Model):
    company = models.OneToOneField(Company, on_delete=models.CASCADE, related_name='settings')
    show_financial_to_client = models.BooleanField(default=False)
    primary_color = models.CharField(max_length=7, default='#C0C0C0')
    custom_domain = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return f"Settings for {self.company.name}"
