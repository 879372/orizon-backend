from django.db import models
from uuid import uuid4

class ExpenseCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, related_name='expense_categories')
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default='#C9A84C')
    is_default = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.company.name})"

class ClientContribution(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='contributions')
    description = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    due_date = models.DateField()
    paid_date = models.DateField(null=True, blank=True)
    installment_number = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pendente'),
        ('paid', 'Pago'),
        ('overdue', 'Atrasado')
    ], default='pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.project.name} - {self.description} ({self.status})"

class Transaction(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='transactions', null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    category = models.ForeignKey(ExpenseCategory, on_delete=models.SET_NULL, null=True, blank=True)
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
