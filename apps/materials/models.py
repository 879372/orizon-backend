from django.db import models
from uuid import uuid4

class Material(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='materials')
    supplier = models.ForeignKey('suppliers.Supplier', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=20)  # m², kg, un, m³, etc.
    quantity_ordered = models.DecimalField(max_digits=10, decimal_places=2)
    quantity_received = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=[
        ('requested', 'Solicitado'),
        ('waiting', 'Aguardando'),
        ('received', 'Recebido'),
        ('used', 'Utilizado'),
    ], default='requested')
    expected_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def total_cost(self):
        return self.quantity_ordered * self.unit_cost
    
    @property
    def is_low_stock(self):
        from decimal import Decimal
        return self.quantity_received < (self.quantity_ordered * Decimal('0.2'))

    def __str__(self):
        return self.name

class MaterialOrder(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE)
    project = models.ForeignKey('projects.Project', on_delete=models.CASCADE, related_name='material_orders')
    description = models.CharField(max_length=255, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Rascunho'),
        ('requested', 'Solicitado'),
        ('approved', 'Aprovado'),
        ('purchased', 'Comprado'),
        ('delivered', 'Entregue')
    ], default='draft')
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def total_value(self):
        return sum(item.total_cost for item in self.items.all())

class MaterialOrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid4, editable=False)
    order = models.ForeignKey(MaterialOrder, on_delete=models.CASCADE, related_name='items')
    name = models.CharField(max_length=200)
    quantity = models.DecimalField(max_digits=10, decimal_places=2)
    unit_cost = models.DecimalField(max_digits=10, decimal_places=2)
    
    @property
    def total_cost(self):
        return self.quantity * self.unit_cost
