from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Company, CompanySettings, Partner
from .serializers import CompanySerializer, CompanySettingsSerializer, PartnerSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsSuperAdmin, IsCompanyAdmin, IsCompanyMember
from apps.projects.models import Project
from apps.employees.models import Employee

class AdminCompanyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdmin]
    queryset = Company.objects.all()
    serializer_class = CompanySerializer

    @action(detail=True, methods=['post'])
    def impersonate(self, request, pk=None):
        company = self.get_object()
        from apps.accounts.models import User
        from apps.accounts.serializers import UserSerializer
        from rest_framework_simplejwt.tokens import RefreshToken

        user = User.objects.filter(company=company).first()
        if not user:
            return Response(
                {"detail": "Nenhum usuário encontrado nesta empresa para impersonação."},
                status=status.HTTP_404_NOT_FOUND
            )

        refresh = RefreshToken.for_user(user)
        return Response({
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': UserSerializer(user).data
        })

class CompanyMeViewSet(viewsets.ViewSet):
    permission_classes = [IsCompanyMember]

    def list(self, request):
        company = request.user.company
        if not company:
            return Response({"detail": "Usuário não associado a uma empresa."}, status=status.HTTP_400_BAD_REQUEST)
        serializer = CompanySerializer(company)
        return Response(serializer.data)

    def partial_update(self, request):
        company = request.user.company
        if not company:
            return Response({"detail": "Usuário não associado a uma empresa."}, status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.role not in ['super_admin', 'company_admin']:
            return Response({"detail": "Permissão negada para alterar dados da empresa."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CompanySerializer(company, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'])
    def stats(self, request):
        company = request.user.company
        if not company:
            return Response({"detail": "Usuário não associado a uma empresa."}, status=status.HTTP_400_BAD_REQUEST)

        projects = Project.objects.filter(company=company)
        employees_count = Employee.objects.filter(company=company, is_active=True).count()
        
        from decimal import Decimal
        total_income = Decimal('0.00')
        total_expense = Decimal('0.00')
        from apps.financial.models import Transaction, ClientContribution
        
        for project in projects:
            project_income = ClientContribution.objects.filter(project=project, status='paid').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            project_expense = Transaction.objects.filter(project=project, type='expense').aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            total_income += project_income
            total_expense += project_expense
            
        total_profit = total_income - total_expense

        partners = Partner.objects.filter(company=company, is_active=True)
        from .serializers import PartnerSerializer
        partners_data = PartnerSerializer(partners, many=True).data

        for p in partners_data:
            base = float(p['base_salary'])
            pct = float(p['profit_percentage'])
            profit_share = float(total_profit) * (pct / 100) if total_profit > 0 else 0
            p['total_calculated'] = base + profit_share

        stats_data = {
            'total_projects': projects.count(),
            'completed_projects': projects.filter(status='completed').count(),
            'in_progress_projects': projects.filter(status='in_progress').count(),
            'delayed_projects': projects.filter(status='delayed').count(),
            'total_budget': projects.aggregate(Sum('total_budget'))['total_budget__sum'] or 0.00,
            'active_employees': employees_count,
            'financial': {
                'total_income': total_income,
                'total_expense': total_expense,
                'total_profit': total_profit
            },
            'partners_distribution': partners_data
        }
        return Response(stats_data)

    @action(detail=False, methods=['get'])
    def dashboard_data(self, request):
        company = request.user.company
        if not company:
            return Response({"detail": "Usuário não associado a uma empresa."}, status=status.HTTP_400_BAD_REQUEST)

        # Re-use stats logic
        stats_response = self.stats(request)
        stats_data = stats_response.data if isinstance(stats_response, Response) else {}

        # Fetch models needed for dashboard only
        from apps.financial.models import Transaction
        from django.db.models import Sum
        import datetime
        from decimal import Decimal

        now = datetime.datetime.now()
        chart_data = []
        for i in range(4, -1, -1):
            d = (now.replace(day=1) - datetime.timedelta(days=1)).replace(day=1) if i > 0 else now.replace(day=1)
            # a safer way to get the month X months ago:
            target_month = now.month - i
            target_year = now.year
            while target_month <= 0:
                target_month += 12
                target_year -= 1
            
            month_str = f"{target_year}-{target_month:02d}"
            month_name_abbr = {1:'Jan',2:'Fev',3:'Mar',4:'Abr',5:'Mai',6:'Jun',7:'Jul',8:'Ago',9:'Set',10:'Out',11:'Nov',12:'Dez'}
            
            faturamento = Transaction.objects.filter(company=company, type='income', date__startswith=month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            gasto = Transaction.objects.filter(company=company, type='expense', date__startswith=month_str).aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00')
            
            chart_data.append({
                "name": month_name_abbr[target_month],
                "Faturamento": float(faturamento),
                "Gasto": float(gasto)
            })

        recent_txs = Transaction.objects.filter(company=company).order_by('-date')[:4]
        recent_activities = []
        for tx in recent_txs:
            recent_activities.append({
                "id": str(tx.id),
                "description": tx.description,
                "amount": float(tx.amount),
                "type": tx.type,
                "date": str(tx.date),
                "categoryName": tx.category.name if tx.category else 'Outros',
                "categoryColor": tx.category.color if tx.category else '#666'
            })

        # Serialize
        data = {
            'stats': stats_data,
            'chartData': chart_data,
            'recentActivities': recent_activities
        }
        return Response(data)

class PartnerViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Partner.objects.all()
    serializer_class = PartnerSerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company)
        else:
            serializer.save()
