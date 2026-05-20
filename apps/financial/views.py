from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember

class TransactionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company, created_by=self.request.user)
        else:
            project = serializer.validated_data.get('project')
            serializer.save(company=project.company, created_by=self.request.user)
