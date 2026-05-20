from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import PhaseCategory, PhaseTask
from .serializers import PhaseCategorySerializer, PhaseTaskSerializer
from core.permissions import IsCompanyMember

class PhaseCategoryViewSet(viewsets.ModelViewSet):
    queryset = PhaseCategory.objects.all()
    serializer_class = PhaseCategorySerializer
    permission_classes = [IsCompanyMember]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        if user.role != 'super_admin':
            qs = qs.filter(project__company=user.company)
        else:
            company_id = self.request.headers.get('X-Company-ID')
            if company_id:
                qs = qs.filter(project__company_id=company_id)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            qs = qs.filter(project_id=project_id)
        return qs

class PhaseTaskViewSet(viewsets.ModelViewSet):
    queryset = PhaseTask.objects.all()
    serializer_class = PhaseTaskSerializer
    permission_classes = [IsCompanyMember]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        if user.role != 'super_admin':
            qs = qs.filter(category__project__company=user.company)
        else:
            company_id = self.request.headers.get('X-Company-ID')
            if company_id:
                qs = qs.filter(category__project__company_id=company_id)
        return qs

    def perform_update(self, serializer):
        serializer.save(updated_by=self.request.user)
