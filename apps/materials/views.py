from rest_framework import viewsets
from .models import Material
from .serializers import MaterialSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember

class MaterialViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company)
        else:
            project = serializer.validated_data.get('project')
            serializer.save(company=project.company)
