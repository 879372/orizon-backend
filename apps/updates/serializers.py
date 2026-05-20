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
    photo_urls = serializers.ListField(child=serializers.CharField(), write_only=True, required=False)

    class Meta:
        model = ProjectUpdate
        fields = [
            'id', 'project', 'title', 'description', 'phase_category',
            'phase_category_name', 'created_by', 'created_by_name', 'created_at', 'photos', 'photo_urls'
        ]
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        photo_urls = validated_data.pop('photo_urls', [])
        update = super().create(validated_data)
        
        import requests
        from django.core.files.temp import NamedTemporaryFile
        from django.core.files import File
        
        for url in photo_urls:
            try:
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    img_temp = NamedTemporaryFile(delete=True)
                    img_temp.write(response.content)
                    img_temp.flush()
                    
                    filename = url.split('/')[-1] or 'photo.jpg'
                    if '?' in filename:
                        filename = filename.split('?')[0]
                    if not filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                        filename = 'photo.jpg'
                        
                    photo = UpdatePhoto(update=update)
                    photo.image.save(filename, File(img_temp), save=True)
            except Exception as e:
                print(f"Error downloading image: {e}")
                
        return update
