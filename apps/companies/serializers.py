from rest_framework import serializers
from .models import Company, CompanySettings

class CompanySettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanySettings
        fields = ['show_financial_to_client', 'primary_color', 'custom_domain']

class CompanySerializer(serializers.ModelSerializer):
    settings = CompanySettingsSerializer(required=False)

    class Meta:
        model = Company
        fields = ['id', 'name', 'cnpj', 'email', 'phone', 'address', 'logo', 'plan', 'is_active', 'created_at', 'settings']
        read_only_fields = ['id', 'created_at']

    def create(self, validated_data):
        settings_data = validated_data.pop('settings', {})
        company = Company.objects.create(**validated_data)
        CompanySettings.objects.create(company=company, **settings_data)
        return company

    def update(self, instance, validated_data):
        settings_data = validated_data.pop('settings', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()

        if settings_data is not None:
            settings_instance, _ = CompanySettings.objects.get_or_create(company=instance)
            for attr, value in settings_data.items():
                setattr(settings_instance, attr, value)
            settings_instance.save()
        return instance
