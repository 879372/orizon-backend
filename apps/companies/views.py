from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Sum
from .models import Company, CompanySettings
from .serializers import CompanySerializer, CompanySettingsSerializer
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
        
        stats_data = {
            'total_projects': projects.count(),
            'completed_projects': projects.filter(status='completed').count(),
            'in_progress_projects': projects.filter(status='in_progress').count(),
            'delayed_projects': projects.filter(status='delayed').count(),
            'total_budget': projects.aggregate(Sum('total_budget'))['total_budget__sum'] or 0.00,
            'active_employees': employees_count,
        }
        return Response(stats_data)
