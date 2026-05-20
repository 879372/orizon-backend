from rest_framework import serializers
from .models import PhaseCategory, PhaseTask

class PhaseTaskSerializer(serializers.ModelSerializer):
    updated_by_name = serializers.CharField(source='updated_by.name', read_only=True)

    class Meta:
        model = PhaseTask
        fields = [
            'id', 'category', 'order', 'name', 'weight_percentage', 'status',
            'start_date', 'end_date', 'notes', 'completed_at', 'updated_by', 'updated_by_name'
        ]
        read_only_fields = ['id', 'completed_at']

class PhaseCategorySerializer(serializers.ModelSerializer):
    tasks = PhaseTaskSerializer(many=True, read_only=True)

    class Meta:
        model = PhaseCategory
        fields = ['id', 'project', 'order', 'name', 'weight_percentage', 'progress_percentage', 'tasks']
        read_only_fields = ['id', 'progress_percentage']
