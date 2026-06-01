from rest_framework import serializers
from .models import User
from apps.companies.serializers import CompanySerializer
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    default_error_messages = {
        'no_active_account': 'E-mail ou senha inválidos'
    }

class UserSerializer(serializers.ModelSerializer):
    company_info = CompanySerializer(source='company', read_only=True)
    linked_projects = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'email', 'name', 'phone', 'role', 'company', 'company_info', 'avatar', 'is_active', 'created_at', 'linked_projects']
        read_only_fields = ['id', 'created_at']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False}
        }

    def create(self, validated_data):
        password = validated_data.pop('password', None)
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if password:
            instance.set_password(password)
        instance.save()
        return instance
    def get_linked_projects(self, obj):
        if obj.role == 'client':
            return [{'id': str(p.id), 'name': p.name} for p in obj.projects.all()]
        return []
