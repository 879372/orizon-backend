from rest_framework import viewsets
from .models import Transaction
from .serializers import TransactionSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember

class TransactionViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsCompanyMember]
