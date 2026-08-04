# pyrefly: ignore [missing-import]
from django.shortcuts import render
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import ApiKey
from .serializers import ApiKeySerializer

# Create your views here.

class ApiKeyListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApiKeySerializer

    def get_queryset(self):
        return ApiKey.objects.filter(user=self.request.user)

class ApiKeyCreateView(generics.CreateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ApiKeySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        key_obj, raw_key = ApiKey.generate_key(request.user, serializer.validated_data['name'])
        response_data = ApiKeySerializer(key_obj).data
        response_data['raw_key'] = raw_key
        return Response(response_data, status=status.HTTP_201_CREATED)

class ApiKeyDeleteView(generics.DestroyAPIView):
    permission_classes = [IsAuthenticated]
    queryset = ApiKey.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        if instance.user != user:
            return Response({'detail': 'You do not have permission to delete this API key'}, status=status.HTTP_403_FORBIDDEN)
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)
