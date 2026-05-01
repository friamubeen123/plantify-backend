from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .serializers import ScanSerializer

from rest_framework_simplejwt.tokens import RefreshToken

from .models import Scan

import numpy as np
from PIL import Image
import tensorflow as tf
import os
import json

# ================= MODEL LOAD =================
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, "plant_model.h5")

model = tf.keras.models.load_model(MODEL_PATH)

labels = [
    "Pepper__bell___Bacterial_spot",
    "Pepper__bell___healthy",
    "Potato___Early_blight",
    "Potato___healthy",
    "Potato___Late_blight",
    "Tomato__Target_Spot",
    "Tomato__Tomato_mosaic_virus",
    "Tomato__Tomato_YellowLeaf__Curl_Virus",
    "Tomato_Bacterial_spot",
    "Tomato_Early_blight",
    "Tomato_healthy",
    "Tomato_Late_blight",
    "Tomato_Leaf_Mold",
    "Tomato_Septoria_leaf_spot",
    "Tomato_Spider_mites_Two_spotted_spider_mite",
]

# ================= LOGIN =================
# ================= LOGIN =================


@csrf_exempt
def login_view(request):
    if request.method != "POST":
        return JsonResponse({"success": False, "error": "Invalid method"}, status=405)

    try:
        data = json.loads(request.body)  # ✅ handle JSON from Flutter
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


# ================= PREDICT =================
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def predict(request):
    image = request.FILES.get("image")

    if image is None:
        return Response({"error": "No image provided"}, status=400)

    img = Image.open(image).resize((224, 224))

    from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
    img = np.array(img)
    img = preprocess_input(img)
    img = np.expand_dims(img, axis=0)

    predictions = model.predict(img)[0]

    top3_idx = predictions.argsort()[-3:][::-1]

    return Response({
        "top3": top3_idx.tolist(),
        "probs": predictions[top3_idx].tolist()
    })


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

    scan = Scan.objects.create(
        user=request.user,
        image=image,
        disease=disease,
        confidence=confidence
    )

    return Response({"message": "Scan saved"})

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_scans(request):
    scans = Scan.objects.filter(user=request.user).order_by('-created_at')
    serializer = ScanSerializer(scans, many=True)
    return Response(serializer.data)
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_scan(request, id):
    try:
        scan = Scan.objects.get(id=id, user=request.user)
        scan.delete()
        return Response({"message": "Deleted"})
    except Scan.DoesNotExist:
        return Response({"error": "Not found"}, status=404)