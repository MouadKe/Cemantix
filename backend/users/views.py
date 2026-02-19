from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics
from .serializers import RegisterSerializer
import json
# Create your views here.

class HelloView(APIView):
    permission_classes = [IsAuthenticated]
    
    
    def get(self, req):
        user = req.user
        
        
        return Response({
            "message": f"Hello Authenticated {user.username}",
            "user": {
                "username": user.username,
                "id": user.id
            }
        })


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer