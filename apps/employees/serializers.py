from rest_framework import serializers
from .models import Employee, Attendance

class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ['id', 'company', 'name', 'role', 'cpf', 'phone', 'email', 'daily_rate', 'is_active', 'avatar', 'created_at']
        read_only_fields = ['id', 'created_at', 'company']

class AttendanceSerializer(serializers.ModelSerializer):
    employee_name = serializers.CharField(source='employee.name', read_only=True)
    employee_role = serializers.CharField(source='employee.role', read_only=True)

    class Meta:
        model = Attendance
        fields = ['employee', 'employee_name', 'employee_role', 'project', 'date', 'present', 'notes']
