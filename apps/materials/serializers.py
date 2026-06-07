from rest_framework import serializers
from .models import Material, MaterialOrder, MaterialOrderItem

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

class MaterialOrderItemSerializer(serializers.ModelSerializer):
    total_cost = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = MaterialOrderItem
        fields = ['id', 'name', 'quantity', 'unit_cost', 'total_cost']
        read_only_fields = ['id', 'total_cost']

class MaterialOrderSerializer(serializers.ModelSerializer):
    items = MaterialOrderItemSerializer(many=True)
    total_value = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = MaterialOrder
        fields = [
            'id', 'company', 'project', 'description', 'status',
            'created_at', 'total_value', 'items'
        ]
        read_only_fields = ['id', 'created_at', 'company', 'total_value']

    def create(self, validated_data):
        items_data = validated_data.pop('items', [])
        order = MaterialOrder.objects.create(**validated_data)
        for item_data in items_data:
            MaterialOrderItem.objects.create(order=order, **item_data)
        return order

    def update(self, instance, validated_data):
        items_data = validated_data.pop('items', None)
        
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.save()

        if items_data is not None:
            instance.items.all().delete()
            for item_data in items_data:
                MaterialOrderItem.objects.create(order=instance, **item_data)
                
        return instance
