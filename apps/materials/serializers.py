from rest_framework import serializers
from .models import Material, MaterialOrder, MaterialOrderItem, MaterialOrderSupplier

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
    class Meta:
        model = MaterialOrderItem
        fields = ['id', 'name', 'quantity', 'unit_value']
        read_only_fields = ['id']

class MaterialOrderSupplierSerializer(serializers.ModelSerializer):
    items = MaterialOrderItemSerializer(many=True)

    class Meta:
        model = MaterialOrderSupplier
        fields = ['id', 'name', 'attachment_url', 'items']
        read_only_fields = ['id']

class MaterialOrderSerializer(serializers.ModelSerializer):
    suppliers = MaterialOrderSupplierSerializer(many=True)

    class Meta:
        model = MaterialOrder
        fields = ['id', 'company', 'project', 'description', 'status', 'expected_date', 'delivery_address', 'created_at', 'suppliers']
        read_only_fields = ['id', 'created_at', 'company']

    def create(self, validated_data):
        suppliers_data = validated_data.pop('suppliers', [])
        order = MaterialOrder.objects.create(**validated_data)
        
        for supplier_data in suppliers_data:
            items_data = supplier_data.pop('items', [])
            supplier = MaterialOrderSupplier.objects.create(order=order, **supplier_data)
            for item_data in items_data:
                MaterialOrderItem.objects.create(supplier=supplier, **item_data)
                
        return order

    def update(self, instance, validated_data):
        suppliers_data = validated_data.pop('suppliers', None)
        
        instance.description = validated_data.get('description', instance.description)
        instance.status = validated_data.get('status', instance.status)
        instance.expected_date = validated_data.get('expected_date', instance.expected_date)
        instance.delivery_address = validated_data.get('delivery_address', instance.delivery_address)
        instance.save()

        if suppliers_data is not None:
            # Recreate suppliers and items
            instance.suppliers.all().delete()
            for supplier_data in suppliers_data:
                items_data = supplier_data.pop('items', [])
                supplier = MaterialOrderSupplier.objects.create(order=instance, **supplier_data)
                for item_data in items_data:
                    MaterialOrderItem.objects.create(supplier=supplier, **item_data)
                
        return instance
