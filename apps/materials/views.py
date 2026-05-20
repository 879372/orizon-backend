from rest_framework import viewsets
from .models import Material
from .serializers import MaterialSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember

class MaterialViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Material.objects.all()
    serializer_class = MaterialSerializer
    permission_classes = [IsCompanyMember]
