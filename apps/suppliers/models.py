from django.db import models
from uuid import uuid4
from django.core.validators import MinValueValidator, MaxValueValidator

class Supplier(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='suppliers')
    name = models.CharField(max_length=200)
    cnpj_cpf = models.CharField(max_length=18, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20)
    category = models.CharField(max_length=20, choices=[
        ('materials', 'Materiais'),
        ('labor', 'Mão de Obra'),
        ('equipment', 'Equipamentos'),
    ])
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        null=True, blank=True
    )
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name
