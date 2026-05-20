from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import KanbanTask
from .serializers import KanbanTaskSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember

class KanbanTaskViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = KanbanTask.objects.all()
    serializer_class = KanbanTaskSerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company)
        else:
            project = serializer.validated_data.get('project')
            serializer.save(company=project.company)

    @action(detail=True, methods=['post'])
    def move(self, request, pk=None):
        task = self.get_object()
        column = request.data.get('column')
        order = request.data.get('order')
        
        if column is not None:
            task.column = column
        if order is not None:
            task.order = int(order)
        
        task.save()
        return Response(KanbanTaskSerializer(task).data)
