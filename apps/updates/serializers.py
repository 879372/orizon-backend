from rest_framework import serializers
from .models import ProjectUpdate, UpdatePhoto

class UpdatePhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = UpdatePhoto
        fields = ['id', 'update', 'image', 'caption', 'order']
        read_only_fields = ['id']

class ProjectUpdateSerializer(serializers.ModelSerializer):
    photos = UpdatePhotoSerializer(many=True, read_only=True)
    created_by_name = serializers.CharField(source='created_by.name', read_only=True)
    phase_category_name = serializers.CharField(source='phase_category.name', read_only=True)

    class Meta:
        model = ProjectUpdate
        fields = [
            'id', 'project', 'title', 'description', 'phase_category',
            'phase_category_name', 'created_by', 'created_by_name', 'created_at', 'photos'
        ]
        read_only_fields = ['id', 'created_at']
