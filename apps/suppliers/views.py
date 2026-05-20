from rest_framework import viewsets
from .models import Supplier
from .serializers import SupplierSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember

class SupplierViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Supplier.objects.all()
    serializer_class = SupplierSerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company)
        else:
            serializer.save()
