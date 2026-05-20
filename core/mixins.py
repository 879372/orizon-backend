class TenantScopedMixin:
    """
    All viewsets inherit this. Automatically scopes all 
    querysets to request.user.company. Super admin bypass.
    """
    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user
        if not user or not user.is_authenticated:
            return qs.none()
        if user.role == 'super_admin':
            company_id = self.request.headers.get('X-Company-ID')
            if company_id:
                return qs.filter(company_id=company_id)
            return qs
        return qs.filter(company=user.company)
