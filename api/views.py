from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Scan
from .serializers import ScanSerializer

import json


# ================= LOGIN =================
@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
    except:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    if not username or not password:
        return JsonResponse({"success": False, "error": "Missing fields"}, status=400)

    user = authenticate(username=username, password=password)

    if user is not None:
        refresh = RefreshToken.for_user(user)

        return JsonResponse({
            "success": True,
            "username": user.username,
            "token": str(refresh.access_token),
        })

    return JsonResponse({"success": False, "error": "Invalid credentials"}, status=401)


# ================= REGISTER =================
@api_view(['POST'])
def register(request):
    username = request.data.get("username")
    password = request.data.get("password")

    if not username or not password:
        return Response({"success": False, "error": "Missing fields"}, status=400)

    if User.objects.filter(username=username).exists():
        return Response({"success": False, "error": "User already exists"}, status=400)

    user = User.objects.create_user(username=username, password=password)

    return Response({
        "success": True,
        "username": user.username
    })


# ================= SAVE SCAN =================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_scan(request):
    image = request.FILES.get('image')
    disease = request.data.get('disease')
    confidence = request.data.get('confidence')

    if not image or not disease or not confidence:
        return Response({"error": "Missing fields"}, status=400)

    Scan.objects.create(
        user=request.user,
        image=image,
        disease=disease,
        confidence=confidence
    )

    return Response({"message": "Scan saved"})


# ================= GET SCANS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scans(request):
    scans = Scan.objects.filter(user=request.user).order_by('-created_at')
    serializer = ScanSerializer(scans, many=True)
    return Response(serializer.data)


# ================= DELETE SCAN =================
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_scan(request, id):
    try:
        scan = Scan.objects.get(id=id, user=request.user)
        scan.delete()
        return Response({"message": "Deleted"})
    except Scan.DoesNotExist:
        return Response({"error": "Not found"}, status=404)