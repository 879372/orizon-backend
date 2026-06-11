from rest_framework import viewsets
from .models import Material, MaterialOrder
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django.core.files.storage import default_storage
from .serializers import MaterialSerializer, MaterialOrderSerializer
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

class MaterialOrderViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = MaterialOrder.objects.all().prefetch_related('items')
    serializer_class = MaterialOrderSerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company)
        else:
            project = serializer.validated_data.get('project')
            serializer.save(company=project.company)

    @action(detail=False, methods=['post'], parser_classes=[MultiPartParser, FormParser])
    def upload_attachment(self, request):
        file_obj = request.FILES.get('file')
        if not file_obj:
            return Response({'error': 'Nenhum arquivo enviado'}, status=400)
        
        file_path = default_storage.save(f'material_receipts/{file_obj.name}', file_obj)
        file_url = default_storage.url(file_path)
        
        return Response({'url': file_url})
