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
    uploaded_photos = serializers.ListField(child=serializers.ImageField(), write_only=True, required=False)

    class Meta:
        model = ProjectUpdate
        fields = [
            'id', 'project', 'title', 'description', 'phase_category',
            'phase_category_name', 'created_by', 'created_by_name', 'created_at', 'photos', 'photo_urls', 'uploaded_photos',
            'video_url', 'video_file'
        ]
        read_only_fields = ['id', 'created_at', 'created_by']

    def create(self, validated_data):
        photo_urls = validated_data.pop('photo_urls', [])
        uploaded_photos = validated_data.pop('uploaded_photos', [])
        update = super().create(validated_data)

        for file in uploaded_photos:
            photo = UpdatePhoto(update=update, image=file)
            photo.save()

        return update

