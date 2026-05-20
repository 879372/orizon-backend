from rest_framework import serializers
from .models import Project
from apps.accounts.serializers import UserSerializer

class ProjectSerializer(serializers.ModelSerializer):
    client_info = UserSerializer(source='client', read_only=True)
    cover_image_url = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = Project
        fields = [
            'id', 'company', 'client', 'client_info', 'name', 'description', 'address',
            'start_date', 'planned_end_date', 'actual_end_date', 'status',
            'total_budget', 'progress_percentage', 'cover_image', 'cover_image_url', 'slug',
            'employees', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'progress_percentage', 'slug', 'created_at', 'updated_at']

    def create(self, validated_data):
        cover_image_url = validated_data.pop('cover_image_url', None)
        project = super().create(validated_data)
        
        if cover_image_url:
            import requests
            from django.core.files.temp import NamedTemporaryFile
            from django.core.files import File
            try:
                response = requests.get(cover_image_url, timeout=10)
                if response.status_code == 200:
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(response.content)
                    img_temp.flush()
                    filename = cover_image_url.split('/')[-1] or 'cover.jpg'
                    if '?' in filename:
                        filename = filename.split('?')[0]
                    if not filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        filename = 'cover.jpg'
                    project.cover_image.save(filename, File(img_temp), save=True)
            except Exception as e:
                print(f"Error downloading cover image: {e}")
        return project
