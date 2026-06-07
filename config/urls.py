from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from apps.accounts.views import MeView, AdminUserViewSet, CustomTokenObtainPairView
from apps.companies.views import AdminCompanyViewSet, CompanyMeViewSet, PartnerViewSet
from apps.projects.views import ProjectViewSet
from apps.phases.views import PhaseCategoryViewSet, PhaseTaskViewSet
from apps.financial.views import TransactionViewSet, ExpenseCategoryViewSet, ClientContributionViewSet, GlobalFinancialSummaryViewSet
from apps.materials.views import MaterialViewSet, MaterialOrderViewSet
from apps.employees.views import EmployeeViewSet
from apps.suppliers.views import SupplierViewSet
from apps.tasks.views import KanbanTaskViewSet
from apps.updates.views import ProjectUpdateViewSet

from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

router = DefaultRouter()
router.register('admin/users', AdminUserViewSet, basename='admin-user')
router.register('admin/companies', AdminCompanyViewSet, basename='admin-company')
router.register('companies/me', CompanyMeViewSet, basename='company-me')
router.register('partners', PartnerViewSet, basename='partner')
router.register('projects', ProjectViewSet, basename='project')
router.register('phases/categories', PhaseCategoryViewSet, basename='phase-category')
router.register('phases/tasks', PhaseTaskViewSet, basename='phase-task')
router.register('transactions', TransactionViewSet, basename='transaction')
router.register('financial/categories', ExpenseCategoryViewSet, basename='expense-category')
router.register('financial/contributions', ClientContributionViewSet, basename='client-contribution')
router.register('financial/global-summary', GlobalFinancialSummaryViewSet, basename='global-financial-summary')
router.register('materials', MaterialViewSet, basename='material')
router.register('material-orders', MaterialOrderViewSet, basename='material-order')
router.register('employees', EmployeeViewSet, basename='employee')
router.register('suppliers', SupplierViewSet, basename='supplier')
router.register('kanban', KanbanTaskViewSet, basename='kanban-task')
router.register('updates', ProjectUpdateViewSet, basename='project-update')

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Auth endpoints
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/auth/me/', MeView.as_view(), name='auth_me'),
    
    # API endpoints
    path('api/', include(router.urls)),
    
    # OpenAPI Schema / Swagger docs
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

from django.views.static import serve
from django.urls import re_path

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
else:
    urlpatterns += [
        re_path(r'^media/(?P<path>.*)$', serve, {'document_root': settings.MEDIA_ROOT}),
    ]
