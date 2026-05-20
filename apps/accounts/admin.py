from django.contrib import admin
from .models import User

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'name', 'role', 'company', 'is_active', 'is_staff')
    list_filter = ('role', 'is_active', 'company')
    search_fields = ('email', 'name')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)
