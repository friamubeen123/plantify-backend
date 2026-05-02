from rest_framework import serializers
from .models import Scan

class ScanSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Scan
        fields = "__all__"

    def get_image(self, obj):
        if obj.image:
            return obj.image.url  # 🔥 THIS FIX
        return None