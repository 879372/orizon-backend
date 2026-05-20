from rest_framework import serializers
from .models import Project
from apps.accounts.serializers import UserSerializer

class ProjectSerializer(serializers.ModelSerializer):
    client_info = UserSerializer(source='client', read_only=True)

    class Meta:
        model = Project
        fields = [
            'id', 'company', 'client', 'client_info', 'name', 'description', 'address',
            'start_date', 'planned_end_date', 'actual_end_date', 'status',
            'total_budget', 'progress_percentage', 'cover_image', 'slug',
            'employees', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'progress_percentage', 'slug', 'created_at', 'updated_at']
