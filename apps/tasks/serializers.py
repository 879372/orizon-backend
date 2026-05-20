from rest_framework import serializers
from .models import KanbanTask

class KanbanTaskSerializer(serializers.ModelSerializer):
    assigned_employee_name = serializers.CharField(source='assigned_to.name', read_only=True)
    phase_task_name = serializers.CharField(source='phase_task.name', read_only=True)

    class Meta:
        model = KanbanTask
        fields = [
            'id', 'project', 'company', 'title', 'description', 'column', 'priority',
            'assigned_to', 'assigned_employee_name', 'phase_task', 'phase_task_name', 'due_date', 'order', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']
