from rest_framework import serializers
from .models import Scan

class ScanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scan
        fields = ["id", "image", "disease", "confidence", "created_at"]
        read_only_fields = ["id", "created_at"]