from rest_framework import viewsets
from .models import Transaction, ExpenseCategory, ClientContribution
from .serializers import TransactionSerializer, ExpenseCategorySerializer, ClientContributionSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember

class ExpenseCategoryViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = ExpenseCategory.objects.all()
    serializer_class = ExpenseCategorySerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company)
        else:
            serializer.save()

class ClientContributionViewSet(viewsets.ModelViewSet):
    queryset = ClientContribution.objects.all()
    serializer_class = ClientContributionSerializer
    permission_classes = [IsCompanyMember]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if user.role != 'super_admin':
            qs = qs.filter(project__company=user.company)
        return qs

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
