from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember
from .models import FlowNode, FlowEdge, FlowNodeItem
from .serializers import FlowNodeSerializer, FlowEdgeSerializer, FlowNodeItemSerializer


class FlowNodeViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FlowNode.objects.all()
    serializer_class = FlowNodeSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project']

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.prefetch_related('items', 'incoming_edges__source')

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        serializer.save(project_id=project_id)

    @action(detail=True, methods=['post'], url_path='items')
    def add_item(self, request, pk=None):
        node = self.get_object()
        serializer = FlowNodeItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(node=node)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """Tenta marcar o nó como concluído. Rejeita se ainda há itens pendentes."""
        node = self.get_object()
        pending_items = node.items.filter(is_done=False).count()
        if pending_items > 0:
            return Response(
                {'detail': f'Ainda há {pending_items} item(s) pendente(s) nesta etapa.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        node.status = 'done'
        node.save(update_fields=['status', 'updated_at'])

        # Atualizar automaticamente o status de nós dependentes que estão bloqueados
        for edge in node.outgoing_edges.select_related('target'):
            target = edge.target
            if target.status == 'blocked' and not target.is_blocked_by_dependencies():
                target.status = 'open'
                target.save(update_fields=['status', 'updated_at'])

        serializer = self.get_serializer(node)
        return Response(serializer.data)


class FlowEdgeViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = FlowEdge.objects.all()
    serializer_class = FlowEdgeSerializer
    permission_classes = [IsCompanyMember]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['project']

    def perform_create(self, serializer):
        project_id = self.request.data.get('project')
        target_id = self.request.data.get('target')

        # Salvar aresta
        edge = serializer.save(project_id=project_id)

        # Ao criar uma dependência, marcar o target como blocked se source ainda não está done
        try:
            from .models import FlowNode
            target_node = FlowNode.objects.get(id=target_id)
            if edge.source.status != 'done' and target_node.status in ('open',):
                target_node.status = 'blocked'
                target_node.save(update_fields=['status', 'updated_at'])
        except FlowNode.DoesNotExist:
            pass


class FlowNodeItemViewSet(viewsets.ModelViewSet):
    queryset = FlowNodeItem.objects.all()
    serializer_class = FlowNodeItemSerializer
    permission_classes = [IsCompanyMember]

    def get_queryset(self):
        """Filtra por nó via query param se fornecido."""
        qs = super().get_queryset()
        node_id = self.request.query_params.get('node')
        if node_id:
            qs = qs.filter(node_id=node_id)
        return qs
