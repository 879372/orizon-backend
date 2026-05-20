from rest_framework import viewsets
from .models import Employee, Attendance
from .serializers import EmployeeSerializer, AttendanceSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember

class EmployeeViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company)
        else:
            serializer.save()
