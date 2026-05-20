from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import ProjectUpdate, UpdatePhoto
from .serializers import ProjectUpdateSerializer, UpdatePhotoSerializer
from core.permissions import IsCompanyMember

class ProjectUpdateViewSet(viewsets.ModelViewSet):
    queryset = ProjectUpdate.objects.all()
    serializer_class = ProjectUpdateSerializer
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
        return qs

    @action(detail=True, methods=['post'])
    def photos(self, request, pk=None):
        update = self.get_object()
        image_file = request.FILES.get('image')
        caption = request.data.get('caption', '')
        order = request.data.get('order', 0)
        
        if not image_file:
            return Response({"detail": "Nenhum arquivo de imagem fornecido."}, status=status.HTTP_400_BAD_REQUEST)
        
        photo = UpdatePhoto.objects.create(
            update=update,
            image=image_file,
            caption=caption,
            order=int(order)
        )
        return Response(UpdatePhotoSerializer(photo).data, status=status.HTTP_201_CREATED)
