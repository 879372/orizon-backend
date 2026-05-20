from rest_framework import viewsets, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import User
from .serializers import UserSerializer
from core.permissions import IsSuperAdmin

class MeView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

class AdminUserViewSet(viewsets.ModelViewSet):
    permission_classes = [IsSuperAdmin]
    queryset = User.objects.all()
    serializer_class = UserSerializer
