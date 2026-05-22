from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Project
from .serializers import ProjectSerializer
from core.mixins import TenantScopedMixin
from core.permissions import IsCompanyMember
from apps.phases.models import PhaseCategory
from apps.phases.serializers import PhaseCategorySerializer

class ProjectViewSet(TenantScopedMixin, viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [IsCompanyMember]

    def perform_create(self, serializer):
        if self.request.user.role != 'super_admin':
            serializer.save(company=self.request.user.company)
        else:
            serializer.save()

    @action(detail=True, methods=['get'])
    def progress(self, request, pk=None):
        project = self.get_object()
        categories = PhaseCategory.objects.filter(project=project)
        categories_data = PhaseCategorySerializer(categories, many=True).data
        return Response({
            'progress_percentage': project.progress_percentage,
            'status': project.status,
            'categories': categories_data
        })

    @action(detail=True, methods=['get'])
    def phases(self, request, pk=None):
        project = self.get_object()
        categories = PhaseCategory.objects.filter(project=project)
        serializer = PhaseCategorySerializer(categories, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='phases/initialize')
    def initialize_phases(self, request, pk=None):
        project = self.get_object()
        from apps.phases.utils import initialize_project_phases
        initialize_project_phases(project)
        return Response({"detail": "Fases inicializadas com sucesso."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'])
    def transactions(self, request, pk=None):
        project = self.get_object()
        from apps.financial.models import Transaction
        from apps.financial.serializers import TransactionSerializer

        if request.method == 'GET':
            transactions = Transaction.objects.filter(project=project)
            if request.user.role != 'super_admin':
                transactions = transactions.filter(company=request.user.company)
            serializer = TransactionSerializer(transactions, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = TransactionSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    project=project,
                    company=request.user.company if request.user.role != 'super_admin' else project.company,
                    created_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'], url_path='financial/summary')
    def financial_summary(self, request, pk=None):
        project = self.get_object()
        from apps.financial.models import Transaction
        from django.db.models import Sum

        transactions = Transaction.objects.filter(project=project)
        if request.user.role != 'super_admin':
            transactions = transactions.filter(company=request.user.company)

        total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0.00
        total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0.00
        balance = total_income - total_expense

        categories = ['labor', 'material', 'equipment', 'other']
        category_summaries = {}
        for cat in categories:
            category_summaries[cat] = transactions.filter(category=cat, type='expense').aggregate(Sum('amount'))['amount__sum'] or 0.00

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance,
            'category_expenses': category_summaries
        })

    @action(detail=True, methods=['get', 'post'])
    def materials(self, request, pk=None):
        project = self.get_object()
        from apps.materials.models import Material
        from apps.materials.serializers import MaterialSerializer

        if request.method == 'GET':
            materials = Material.objects.filter(project=project)
            if request.user.role != 'super_admin':
                materials = materials.filter(company=request.user.company)
            serializer = MaterialSerializer(materials, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = MaterialSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    project=project,
                    company=request.user.company if request.user.role != 'super_admin' else project.company
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get'])
    def employees(self, request, pk=None):
        project = self.get_object()
        employees = project.employees.all()
        from apps.employees.serializers import EmployeeSerializer
        serializer = EmployeeSerializer(employees, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='employees/(?P<emp_id>[-\\w]+)/assign')
    def assign_employee(self, request, pk=None, emp_id=None):
        project = self.get_object()
        from apps.employees.models import Employee
        try:
            employee = Employee.objects.get(id=emp_id)
        except Employee.DoesNotExist:
            return Response({"detail": "Funcionário não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        if request.user.role != 'super_admin' and employee.company != request.user.company:
            return Response({"detail": "Permissão negada."}, status=status.HTTP_403_FORBIDDEN)
        
        project.employees.add(employee)
        return Response({"detail": f"Funcionário {employee.name} associado com sucesso."}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['get', 'post'])
    def attendance(self, request, pk=None):
        project = self.get_object()
        from apps.employees.models import Attendance
        from apps.employees.serializers import AttendanceSerializer

        if request.method == 'GET':
            date_str = request.query_params.get('date')
            attendances = Attendance.objects.filter(project=project)
            if date_str:
                attendances = attendances.filter(date=date_str)
            serializer = AttendanceSerializer(attendances, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            data = request.data
            if isinstance(data, list):
                serializer = AttendanceSerializer(data=data, many=True)
                if serializer.is_valid():
                    for item in serializer.validated_data:
                        Attendance.objects.update_or_create(
                            employee=item['employee'],
                            project=project,
                            date=item['date'],
                            defaults={'present': item['present'], 'notes': item.get('notes', '')}
                        )
                    return Response({"detail": "Presenças registradas com sucesso."}, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            else:
                serializer = AttendanceSerializer(data=data)
                if serializer.is_valid():
                    Attendance.objects.update_or_create(
                        employee=serializer.validated_data['employee'],
                        project=project,
                        date=serializer.validated_data['date'],
                        defaults={'present': serializer.validated_data['present'], 'notes': serializer.validated_data.get('notes', '')}
                    )
                    return Response(serializer.data, status=status.HTTP_200_OK)
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['get', 'post'])
    def kanban(self, request, pk=None):
        project = self.get_object()
        from apps.tasks.models import KanbanTask
        from apps.tasks.serializers import KanbanTaskSerializer

        if request.method == 'GET':
            tasks = KanbanTask.objects.filter(project=project)
            if request.user.role != 'super_admin':
                tasks = tasks.filter(company=request.user.company)
            serializer = KanbanTaskSerializer(tasks, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = KanbanTaskSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    project=project,
                    company=request.user.company if request.user.role != 'super_admin' else project.company
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='by-slug/(?P<slug>[-\\w]+)', permission_classes=[permissions.AllowAny])
    def by_slug(self, request, slug=None):
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'])
    def updates(self, request, pk=None):
        project = self.get_object()
        from apps.updates.models import ProjectUpdate
        from apps.updates.serializers import ProjectUpdateSerializer

        if request.method == 'GET':
            updates = ProjectUpdate.objects.filter(project=project)
            if request.user.role != 'super_admin':
                updates = updates.filter(project__company=request.user.company)
            serializer = ProjectUpdateSerializer(updates, many=True)
            return Response(serializer.data)
        
        elif request.method == 'POST':
            serializer = ProjectUpdateSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(
                    project=project,
                    created_by=request.user
                )
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='portal/(?P<slug>[-\\w]+)/overview', permission_classes=[permissions.AllowAny])
    def portal_overview(self, request, slug=None):
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = ProjectSerializer(project)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='portal/(?P<slug>[-\\w]+)/updates', permission_classes=[permissions.AllowAny])
    def portal_updates(self, request, slug=None):
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        from apps.updates.models import ProjectUpdate
        from apps.updates.serializers import ProjectUpdateSerializer
        updates = ProjectUpdate.objects.filter(project=project)
        serializer = ProjectUpdateSerializer(updates, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='portal/(?P<slug>[-\\w]+)/financial', permission_classes=[permissions.AllowAny])
    def portal_financial(self, request, slug=None):
        try:
            project = Project.objects.select_related('company').get(slug=slug)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        from apps.companies.models import CompanySettings
        settings = CompanySettings.objects.filter(company=project.company).first()
        if not settings or not settings.show_financial_to_client:
            return Response({"detail": "Informações financeiras não compartilhadas com o cliente."}, status=status.HTTP_403_FORBIDDEN)
        
        from apps.financial.models import Transaction
        from django.db.models import Sum
        transactions = Transaction.objects.filter(project=project)
        total_income = transactions.filter(type='income').aggregate(Sum('amount'))['amount__sum'] or 0.00
        total_expense = transactions.filter(type='expense').aggregate(Sum('amount'))['amount__sum'] or 0.00
        balance = total_income - total_expense

        return Response({
            'total_income': total_income,
            'total_expense': total_expense,
            'balance': balance
        })

    @action(detail=False, methods=['get'], url_path='public/(?P<project_id>[-\\w]+)/evolution', permission_classes=[permissions.AllowAny])
    def public_evolution(self, request, project_id=None):
        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"detail": "Projeto não encontrado."}, status=status.HTTP_404_NOT_FOUND)
        
        # Obter dados básicos do projeto
        project_data = ProjectSerializer(project).data
        
        # Obter etapas
        from apps.phases.models import PhaseCategory
        from apps.phases.serializers import PhaseCategorySerializer
        categories = PhaseCategory.objects.filter(project=project)
        categories_data = PhaseCategorySerializer(categories, many=True).data

        # Obter atualizações (Diário)
        from apps.updates.models import ProjectUpdate
        from apps.updates.serializers import ProjectUpdateSerializer
        updates = ProjectUpdate.objects.filter(project=project).order_by('-created_at')
        updates_data = ProjectUpdateSerializer(updates, many=True).data

        return Response({
            'project': project_data,
            'categories': categories_data,
            'updates': updates_data
        })
