from rest_framework import serializers
from .models import Transaction, ExpenseCategory, ClientContribution

class ExpenseCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ExpenseCategory
        fields = ['id', 'company', 'name', 'color', 'is_default', 'is_active']
        read_only_fields = ['id', 'company', 'is_default']

class ClientContributionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ClientContribution
        fields = [
            'id', 'project', 'description', 'amount', 'due_date',
            'paid_date', 'installment_number', 'status', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    category_color = serializers.CharField(source='category.color', read_only=True)

    class Meta:
        model = Transaction
        fields = [
            'id', 'project', 'company', 'category', 'category_name', 'category_color', 'type', 'description',
            'amount', 'date', 'receipt', 'supplier', 'supplier_name', 'created_by', 'created_by_name', 'created_at'
        ]
        read_only_fields = ['id', 'created_at', 'company', 'created_by']
