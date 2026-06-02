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
        
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
            
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

from rest_framework.response import Response
from django.db.models import Sum

class GlobalFinancialSummaryViewSet(viewsets.ViewSet):
    permission_classes = [IsCompanyMember]

    def list(self, request):
        company = request.user.company
        project_id = request.query_params.get('project_id')
        
        # 1. Filter queries
        expenses_qs = Transaction.objects.filter(company=company, type='expense')
        incomes_generic_qs = Transaction.objects.filter(company=company, type='income', project__isnull=True)
        contributions_qs = ClientContribution.objects.filter(project__company=company)

        if project_id:
            expenses_qs = expenses_qs.filter(project_id=project_id)
            contributions_qs = contributions_qs.filter(project_id=project_id)
            incomes_generic_qs = incomes_generic_qs.none()

        # 2. Aggregations
        total_expense = expenses_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        total_contributions = contributions_qs.filter(status='paid').aggregate(Sum('amount'))['amount__sum'] or 0
        total_generic_income = incomes_generic_qs.aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_income = total_contributions + total_generic_income
        balance = total_income - total_expense

        # 3. Expenses by Category
        expenses_by_category = {}
        for exp in expenses_qs:
            cat_name = exp.category.name if exp.category else 'Outros'
            cat_color = exp.category.color if exp.category else '#888888'
            if cat_name not in expenses_by_category:
                expenses_by_category[cat_name] = {'name': cat_name, 'value': 0, 'color': cat_color}
            expenses_by_category[cat_name]['value'] += float(exp.amount)
            
        chart_data = list(expenses_by_category.values())

        # 4. Ledger (Extrato)
        ledger_items = []
        for exp in expenses_qs:
            ledger_items.append({
                'id': str(exp.id),
                'description': exp.description,
                'date': str(exp.date),
                'categoryName': exp.category.name if exp.category else 'Outros',
                'categoryColor': exp.category.color if exp.category else '#888888',
                'projectName': exp.project.name if exp.project else 'Geral da Empresa',
                'type': 'expense',
                'amount': float(exp.amount),
                'status': 'paid'
            })
            
        for inc in incomes_generic_qs:
            ledger_items.append({
                'id': str(inc.id),
                'description': inc.description,
                'date': str(inc.date),
                'categoryName': inc.category.name if inc.category else 'Aporte',
                'categoryColor': inc.category.color if inc.category else '#10b981',
                'projectName': 'Geral da Empresa',
                'type': 'income',
                'amount': float(inc.amount),
                'status': 'paid'
            })
            
        for cont in contributions_qs:
            ledger_items.append({
                'id': str(cont.id),
                'description': cont.description or f"Aporte Parcela {cont.installment_number}",
                'date': str(cont.due_date),
                'categoryName': 'Aporte',
                'categoryColor': '#10b981',
                'projectName': cont.project.name,
                'type': 'income',
                'amount': float(cont.amount),
                'status': cont.status
            })

        # Sort ledger by date descending
        ledger_items.sort(key=lambda x: x['date'], reverse=True)
        
        # Limit to 100 items for performance
        ledger_items = ledger_items[:100]

        return Response({
            'total_income': float(total_income),
            'total_expense': float(total_expense),
            'balance': float(balance),
            'expenses_by_category': chart_data,
            'ledger': ledger_items
        })
