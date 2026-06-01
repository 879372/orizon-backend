from django.db import models
from uuid import uuid4
from core.fields import CompressedImageField

class Company(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    name = models.CharField(max_length=200)
    cnpj = models.CharField(max_length=18, unique=True)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    logo = CompressedImageField(upload_to='logos/', null=True, blank=True, max_width=600, max_height=600)
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

class Partner(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='partners')
    name = models.CharField(max_length=100)
    base_salary = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    profit_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company.name})"
