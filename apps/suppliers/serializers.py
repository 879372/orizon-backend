from rest_framework import serializers
from .models import Supplier

class SupplierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Supplier
        fields = ['id', 'company', 'name', 'cnpj_cpf', 'email', 'phone', 'category', 'rating', 'notes', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at', 'company']
