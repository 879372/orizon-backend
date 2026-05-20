from django.db import models
from uuid import uuid4

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='transactions')
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    category = models.CharField(max_length=20, choices=[
        ('labor', 'Mão de Obra'),
        ('material', 'Material'),
        ('equipment', 'Equipamentos'),
        ('other', 'Outros'),
    ])
    type = models.CharField(max_length=10, choices=[('income', 'Entrada'), ('expense', 'Saída')])
    description = models.CharField(max_length=300)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    receipt = models.FileField(upload_to='receipts/', null=True, blank=True)
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey('accounts.User', on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.type.upper()} - {self.description} ({self.amount})"
