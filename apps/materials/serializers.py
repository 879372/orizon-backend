from rest_framework import serializers
from .models import Material

class MaterialSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
    is_low_stock = serializers.BooleanField(read_only=True)

    class Meta:
        model = Material
        fields = [
            'id', 'company', 'project', 'supplier', 'supplier_name', 'name', 'unit',
            'quantity_ordered', 'quantity_received', 'unit_cost', 'total_cost',
            'status', 'expected_date', 'is_low_stock', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'company']
